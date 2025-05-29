import concurrent.futures
import threading
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from services.coda_service import add_row, add_rows_batch
from configs.config import getenv
from db.mongo import Database
from util.dataclass import (
    Execucao,
    Fatura,
    NotificationDetail,
    Processo,
    StatusExecucao,
    WebhookPayload,
)
from util.log import Logs
from util.dataclass import EmailConfig, NotificationType
from services.email_service import LegacyGmailService
from services.notification_service import NotificationService

logger = Logs.return_log(__name__)


class ProcessManager:
    def __init__(self):
        # Keep original initialization
        self.db = Database()
        # Thread-local storage for thread-safe DB connections
        self._thread_local = threading.local()
        # Thread pool for parallel operations
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        try:
            self.gmail_service = LegacyGmailService()
            self.email_config = self.gmail_service.email_config
            logger.debug(
                f"Serviço de e-mail configurado com sucesso: {self.email_config.user_email}"
            )
        except:
            self.gmail_service = None
            pass

    # Thread-safe database getter
    def _get_db(self):
        if not hasattr(self._thread_local, 'db'):
            self._thread_local.db = Database()
        return self._thread_local.db

    def notify(
        self,
        processo_id: str,
        notification_type: NotificationType,
        status: StatusExecucao,
        erro: Optional[str] = None,
        quantidade: Optional[int] = None,
    ):
        cliente, servico, dados_sat, operadora = self.get_info_cadastro(
            processo_id)
        notification_service = NotificationService(self.gmail_service)
        success_notification = notification_type
        notification_detail = NotificationDetail(
            cliente=cliente,
            servico=servico,
            servico_sat=dados_sat,
            operadora=operadora,
            processo=processo_id,
            status=status,
            erro=erro,
            quantidade=quantidade,
        )
        notification_service.send_notification(
            recipients=["tiagopereiraramos@gmail.com"],
            notification_type=success_notification,
            notification_detail=notification_detail,
        )

    def create_all_process(self, pesquisa_processo: str = "", operadora: str = "") -> list:
        process = []
        try:
            # Usar match para criar um comportamento de switch-case
            match (bool(pesquisa_processo), bool(operadora)):
                case (True, True):
                    # Caso 1: Com hash_execucao e operadora específicos
                    cadastro = self.db.cadastro.read({
                        "hash_cron_cad": pesquisa_processo,
                        "operadora": operadora
                    })
                    if cadastro:
                        processo = self.db.processo.read({
                            "hash_execucao": pesquisa_processo,
                            "mes_ano": datetime.now().strftime("%Y-%m"),
                        })
                        if not processo:
                            processo_id, hash_execucao = self.create_process(
                                pesquisa_processo, sat=True
                            )
                            logger.info(
                                f"Novo processo criado: {processo_id}, Hash: {cadastro.hash_cron_cad}, Operadora: {cadastro.operadora}"
                            )
                            process.append(self.return_process(
                                processo_id=processo_id, hash_execucao=cadastro.hash_cron_cad))
                        else:
                            processo_id = processo.processo_id
                            logger.info(
                                f"Processo já existente: {processo.processo_id}, Hash: {processo.hash_execucao}, Operadora: {cadastro.operadora}"
                            )
                            if processo.status_final == StatusExecucao.UPLOADED_SAT.value:
                                logger.info(
                                    f"Processo {processo.processo_id} já foi marcado como 'UPLOADED_SAT'. Nenhuma nova execução será criada."
                                )
                                return None
                            process.append(self.return_process(
                                processo_id=processo_id, hash_execucao=processo.hash_execucao))

                case (True, False):
                    # Caso 2: Com apenas hash_execucao específico
                    cadastro = self.db.cadastro.read(
                        {"hash_cron_cad": pesquisa_processo})
                    if cadastro:
                        processo = self.db.processo.read({
                            "hash_execucao": pesquisa_processo,
                            "mes_ano": datetime.now().strftime("%Y-%m"),
                        })
                        if not processo:
                            processo_id, hash_execucao = self.create_process(
                                pesquisa_processo, sat=True
                            )
                            logger.info(
                                f"Novo processo criado: {processo_id}, Hash: {cadastro.hash_cron_cad}, Operadora: {cadastro.operadora}"
                            )
                            process.append(self.return_process(
                                processo_id=processo_id, hash_execucao=cadastro.hash_cron_cad))
                        else:
                            processo_id = processo.processo_id
                            logger.info(
                                f"Processo já existente: {processo.processo_id}, Hash: {processo.hash_execucao}, Operadora: {cadastro.operadora}"
                            )
                            if processo.status_final == StatusExecucao.UPLOADED_SAT.value:
                                logger.info(
                                    f"Processo {processo.processo_id} já foi marcado como 'UPLOADED_SAT'. Nenhuma nova execução será criada."
                                )
                                return None
                            process.append(self.return_process(
                                processo_id=processo_id, hash_execucao=processo.hash_execucao))

                case (False, True):
                    # Caso 3: Com apenas operadora específica
                    # Use threading for multiple processes
                    cadastros = self.db.cadastro.read({"operadora": operadora})
                    process = self._process_cadastros_parallel(cadastros)

                case (False, False):
                    # Caso 4: Sem parâmetros - processa todos os cadastros
                    # Use threading for multiple processes
                    cadastros = self.db.cadastro.read({})
                    process = self._process_cadastros_parallel(cadastros)

            return process
        except Exception as e:
            logger.critical(f"Erro ao ler cadastros: {e}")
            return None

    def _process_cadastros_parallel(self, cadastros):
        """Process multiple cadastros in parallel using threads"""
        if not cadastros:
            return []

        # Ensure cadastros is a list
        cadastros = cadastros if isinstance(cadastros, list) else [cadastros]

        logger.debug(f"Processando {len(cadastros)} cadastros em paralelo")

        # List to store valid processes
        result_processes = []

        # Submit all tasks and collect futures
        futures = []
        for cad in cadastros:
            futures.append(self._executor.submit(
                self._process_single_cadastro, cad))

        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    result_processes.append(result)
            except Exception as e:
                logger.error(f"Erro em processamento paralelo: {e}")

        return result_processes

    def _process_single_cadastro(self, cad):
        """Process a single cadastro in a thread-safe way"""
        try:
            # Use thread-local DB connection
            db = self._get_db()

            processo = db.processo.read({
                "hash_execucao": cad.hash_cron_cad,
                "mes_ano": datetime.now().strftime("%Y-%m"),
            })

            if not processo:
                processo_id, hash_execucao = self.create_process(
                    cad.hash_cron_cad
                )
                logger.info(
                    f"Novo processo criado: {processo_id}, Hash: {cad.hash_cron_cad}, Operadora: {cad.operadora}"
                )
                return self.return_process(
                    processo_id=processo_id, hash_execucao=cad.hash_cron_cad)
            else:
                processo_id = processo.processo_id
                logger.info(
                    f"Processo já existente: {processo.processo_id}, Hash: {processo.hash_execucao}, Operadora: {cad.operadora}"
                )
                if processo.status_final == StatusExecucao.UPLOADED_SAT.value:
                    logger.info(
                        f"Processo {processo.processo_id} já foi marcado como 'UPLOADED_SAT'. Nenhuma nova execução será criada."
                    )
                    return None
                return self.return_process(
                    processo_id=processo_id, hash_execucao=processo.hash_execucao)
        except Exception as e:
            logger.error(f"Erro ao processar cadastro {cad}: {e}")
            return None

    def create_process(self, hash_execucao, sat=False):
        try:
            processo_id = self.db.generate_process_id(
                f"TPSM-{datetime.now().strftime('%Y-%m')}"
            )
            processo = Processo(
                processo_id=processo_id,
                hash_execucao=hash_execucao,
                execucoes=[],
                status_final=(
                    StatusExecucao.CREATED.value
                    if not sat
                    else StatusExecucao.COMPLETED.value
                ),
                criado_em=datetime.now(timezone.utc),
                faturas=[],
                mes_ano=datetime.now().strftime("%Y-%m"),
            )

            self.db.processo.create(processo)
            logger.info(
                f"Novo processo criado: {processo_id}, Hash: {hash_execucao}")

            return processo_id, hash_execucao
        except Exception as e:
            logger.error(f"Erro ao processar cadastro {e}")
            return None, None

    def add_execucao_processo(self, processo_id, execucao):
        """
        Atualiza o processo adicionando apenas o campo 'session_id' à lista de execuções.
        """
        pipeline = [
            {
                "$set": {
                    "execucoes": {
                        "$cond": {
                            "if": {"$eq": [{"$type": "$execucoes"}, "array"]},
                            "then": {
                                "$concatArrays": [
                                    "$execucoes",
                                    [{"session_id": execucao.session_id}],
                                ]
                            },
                            "else": [{"session_id": execucao.session_id}],
                        }
                    }
                }
            }
        ]

        self.db.processo.update(
            {"processo_id": processo_id},
            pipeline,
        )
        logger.info(
            f"Processo {processo_id} atualizado com a nova session_id.")

    def create_execucao(
        self,
        processo_id,
        hash_execucao,
        status=StatusExecucao.PENDING,
        nao_cria_sat=False,
    ):
        try:
            # Tenta buscar o processo no banco de dados
            processo = self.db.processo.read({"processo_id": processo_id})

            # Verifica se o processo foi encontrado
            if processo:
                # Verifica o status final do processo
                # Gera o session_id único para a execução
                session_id = self.db.generate_session_id(hash_execucao)

                match processo.status_final:
                    case StatusExecucao.COMPLETED.value:
                        if (
                            self.get_faturas_processo(processo_id=processo_id)
                            and nao_cria_sat == False
                        ):
                            logger.warning(
                                "Já existe uma fatura para esse processo. Nenhuma nova execução será criada."
                            )
                            return None
                        else:
                            etapa = "UPLOAD SAT"
                    case StatusExecucao.UPLOADED_SAT.value:
                        logger.warning(
                            f"Processo {processo_id} já foi marcado como 'UPLOADED_SAT'. Nenhuma nova execução será criada."
                        )
                        return None
                    case _:
                        etapa = "DOWNLOAD SAT"

                # Cria uma nova instância de Execucao
                execucao = Execucao(
                    session_id=session_id,
                    hash_execucao=hash_execucao,
                    processo_id=processo_id,
                    etapa=etapa,
                    status=status.value,  # Converte enum para string
                    data_inicio=datetime.now(timezone.utc),
                )

                # Cria a execução no banco de dados
                self.db.execucao.create(execucao)
                logger.info(
                    f"Execução criada com sucesso: {execucao.session_id}")
                self.add_execucao_processo(processo_id, execucao)

                return execucao

            else:
                logger.error(f"Processo com ID {processo_id} não encontrado.")
                raise Exception(f"Processo {processo_id} não encontrado.")

        except Exception as e:
            # Loga qualquer erro que ocorrer durante o processo de criação
            logger.error(
                f"Erro ao criar execução para o processo {processo_id}: {e}")
            raise

    def create_fatura(self, processo_id, nome_arquivo, vencimento):
        try:
            # Tratar a data recebida
            data_vencimento_formatada = self._formatar_data_vencimento(
                vencimento)

            # Criação da instância da fatura
            fatura = Fatura(
                caminho=nome_arquivo,
                data_vencimento=data_vencimento_formatada,
            )

            # Resto do código permanece igual...
            fatura_dict = fatura.to_json()
            pipeline = [
                {
                    "$set": {
                        "faturas": {
                            "$concatArrays": [
                                "$faturas",
                                [fatura_dict],
                            ]
                        }
                    }
                }
            ]

            self.db.processo.update(
                {"processo_id": processo_id},
                pipeline,
            )

            logger.info(
                f"Fatura criada e adicionada ao processo {processo_id} com sucesso.")
            return fatura.to_json()

        except Exception as e:
            logger.error(
                f"Erro ao criar fatura para o processo {processo_id}: {e}")
            raise

    def _formatar_data_vencimento(self, vencimento):
        """
        Formata a data de vencimento para o formato aceito pelo modelo Fatura.

        Args:
            vencimento (str): Data de vencimento em vários formatos possíveis

        Returns:
            str: Data formatada como DD/MM/YYYY
        """
        from datetime import datetime

        # Se já for um objeto datetime, converte para string no formato padrão
        if isinstance(vencimento, datetime):
            return vencimento.strftime("%d/%m/%Y")

        # Remove possíveis espaços extras
        vencimento = vencimento.strip()

        # Detecta formato com ano de 2 dígitos (16/05/25)
        if len(vencimento) == 8 and vencimento.count('/') == 2:
            dia, mes, ano_curto = vencimento.split('/')
            # Assume que anos menores que 50 são do século 21, maiores são do século 20
            if int(ano_curto) < 50:
                ano_completo = f"20{ano_curto}"
            else:
                ano_completo = f"19{ano_curto}"
            return f"{dia}/{mes}/{ano_completo}"

        # Trata formato YYYY-MM-DD
        elif len(vencimento) == 10 and vencimento.count('-') == 2:
            ano, mes, dia = vencimento.split('-')
            if len(ano) == 4:  # YYYY-MM-DD
                return f"{dia}/{mes}/{ano}"

        # Formato DD-MM-YYYY
        elif len(vencimento) == 10 and vencimento.count('-') == 2:
            dia, mes, ano = vencimento.split('-')
            if len(ano) == 4:  # DD-MM-YYYY
                return f"{dia}/{mes}/{ano}"

        # Formato já correto DD/MM/YYYY
        elif len(vencimento) == 10 and vencimento.count('/') == 2:
            dia, mes, ano = vencimento.split('/')
            if len(ano) == 4:  # DD/MM/YYYY
                return vencimento

        # Formato YYYY/MM/DD
        elif len(vencimento) == 10 and vencimento.count('/') == 2:
            ano, mes, dia = vencimento.split('/')
            if len(ano) == 4:  # YYYY/MM/DD
                return f"{dia}/{mes}/{ano}"

        # Se nenhum formato conhecido for identificado, retorna como está
        # (o modelo Fatura irá validar e gerar o erro apropriado)
        return vencimento

    def get_faturas_processo(self, processo_id: str) -> Optional[list]:
        try:
            # Busca o processo no banco de dados
            processo = self.db.processo.read({"processo_id": processo_id})

            if processo:
                # Recupera a lista de faturas do processo
                faturas = processo.faturas

                if faturas:
                    logger.info(
                        f"Faturas recuperadas para o processo {processo_id}.")
                    return faturas
                else:
                    logger.warning(
                        f"Não há faturas associadas ao processo {processo_id}."
                    )
                    return []
            else:
                logger.error(f"Processo com ID {processo_id} não encontrado.")
                return []

        except Exception as e:
            # Loga qualquer erro ocorrido ao tentar recuperar as faturas
            logger.error(
                f"Erro ao recuperar faturas para o processo {processo_id}: {e}"
            )
            return []

    def update_status_execucao(
        self,
        processo_id,
        session_id,
        novo_status: StatusExecucao,
        detalhes=None,
    ):
        try:
            # Busca o processo no banco de dados
            execucao = self.db.execucao.read(
                {"session_id": session_id, "processo_id": processo_id}
            )
            if execucao:
                # Atualiza o status da execução
                if not detalhes:
                    self.db.execucao.update(
                        {"session_id": session_id, "processo_id": processo_id},
                        {
                            "status": novo_status.value,
                            "data_fim": datetime.now(timezone.utc),
                        },
                    )
                    logger.info(
                        f"Status da execução {session_id} atualizado para {novo_status.name}."
                    )
                    return True
                else:
                    self.db.execucao.update(
                        {"session_id": session_id, "processo_id": processo_id},
                        {
                            "status": novo_status.value,
                            "detalhes": detalhes,
                            "data_fim": datetime.now(timezone.utc),
                        },
                    )
                    logger.info(
                        f"Status da execução {session_id} atualizado para {novo_status.name}, com o detalhe: {detalhes}."
                    )
                    return True

        except Exception as e:
            # Loga qualquer erro ocorrido ao tentar buscar a execução
            logger.error(
                f"Erro ao buscar execução para a execucao {session_id}: {e}")
            raise

    def update_status_processo(
        self, processo_id, novo_status: StatusExecucao, detalhes=None, webhookpayload: WebhookPayload = None
    ):
        try:
            # Busca o processo no banco de dados
            status_notificacao = NotificationType.SUCCESS
            processo = self.db.processo.read({"processo_id": processo_id})
            if processo:
                # Atualiza o status da execução
                match novo_status:
                    case StatusExecucao.COMPLETED | StatusExecucao.UPLOADED_SAT:
                        query = {
                            "status_final": novo_status.value,
                            "finalizado_em": datetime.now(timezone.utc),
                        }
                        status_notificacao = NotificationType.SUCCESS
                    case _:
                        query = {"status_final": novo_status.value}
                        status_notificacao = NotificationType.FAILURE

                self.db.processo.update({"processo_id": processo_id}, query)
                logger.info(
                    f"Status do processo {processo_id} atualizado para {novo_status.name}."
                )

                if self.gmail_service:
                    logger.info(
                        f"Enviando e-mail de notificação para o processo: {processo_id}."
                    )
                    self.notify(
                        processo_id=processo_id,
                        notification_type=status_notificacao,
                        status=novo_status,
                        erro=detalhes,
                    )

                return True

        except Exception as e:
            # Loga qualquer erro ocorrido ao tentar buscar a execução
            logger.error(
                f"Erro ao buscar execução para o processo {processo_id}: {e}")
            raise

    def get_info_fatura(self, processo_id):
        try:
            processo = self.db.processo.read({"processo_id": processo_id})
            if processo:
                faturas = processo.faturas
                if faturas:
                    logger.info(
                        f"Faturas recuperadas para o processo {processo_id}.")
                    # Convertendo para datetime
                    data_formatada = datetime.strptime(
                        faturas[0]["data_vencimento"], "%Y-%m-%dT%H:%M:%S"
                    )

                    # Convertendo para string no formato desejado
                    data_formatada_str = data_formatada.strftime("%d/%m/%Y")
                    return faturas[0]["caminho"], data_formatada_str
                else:
                    logger.warning(
                        f"Não há faturas associadas ao processo {processo_id}."
                    )
                    return []
            else:
                logger.error(f"Processo com ID {processo_id} não encontrado.")
                return []
        except Exception as e:
            logger.error(
                f"Erro ao recuperar faturas para o processo {processo_id}: {e}"
            )
            return []

    def get_info_cadastro(self, processo_id):
        try:
            processo = self.db.processo.read({"processo_id": processo_id})
            cadastro = self.db.cadastro.read(
                {"hash_cron_cad": processo.hash_execucao})
            if cadastro:
                cliente, servico, dados_sat, operadora = (
                    cadastro.razao,
                    cadastro.servico,
                    cadastro.dados_sat,
                    cadastro.operadora,
                )
                return cliente, servico, dados_sat, operadora
            else:
                logger.error(
                    f"Cadastro com hash {processo_id} não encontrado.")
                return None
        except Exception as e:
            logger.error(
                f"Erro ao recuperar cadastro com o processo: {processo_id}: {e}"
            )
            return None

    def get_info_cadastro_coda(self, processo_id):
        try:
            processo = self.db.processo.read({"processo_id": processo_id})
            mes_ano = processo.mes_ano
            cadastro = self.db.cadastro.read(
                {"hash_cron_cad": processo.hash_execucao})
            if cadastro:
                cnpj_mascara, cnpj, nome_pesquisa_sat, operadora, servico, filial, filtro = (
                    cadastro.cnpj_mascara,
                    cadastro.cnpj,
                    cadastro.nome_filtro,
                    cadastro.operadora,
                    cadastro.servico,
                    cadastro.unidade,
                    cadastro.filtro,
                )
                return cnpj_mascara, cnpj, nome_pesquisa_sat, operadora, servico, filial, filtro, mes_ano
            else:
                logger.error(
                    f"Cadastro com hash {processo_id} não encontrado.")
                return None
        except Exception as e:
            logger.error(
                f"Erro ao recuperar cadastro com o processo: {processo_id}: {e}"
            )
            return None

    def return_sat_process(self):
        """Multithreaded version to get SAT processes"""
        lista_processos = []
        processos = self.db.processo.read({"status_final": "COMPLETED"})

        if processos:
            processos = processos if isinstance(
                processos, list) else [processos]

            # Process in parallel
            futures = []
            for p in processos:
                futures.append(self._executor.submit(
                    self._process_sat_item, p))

            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        lista_processos.append(result)
                except Exception as e:
                    logger.error(f"Erro em processamento paralelo de SAT: {e}")

        return lista_processos

    def _process_sat_item(self, p):
        """Process a single SAT item in a thread"""
        try:
            # Garante que há faturas e pega a primeira, se existir
            fatura = p.faturas[0] if p.faturas else None
            cnpj_mascara, cnpj, nome_pesquisa_sat, operadora, servico, filial, filtro, mes_ano = self.get_info_cadastro_coda(
                p.processo_id)
            return {
                "processo_id": p.processo_id,
                "hash_execucao": p.hash_execucao,
                "caminho": fatura["caminho"] if fatura else None,
                "data_vencimento": (fatura["data_vencimento"] if fatura else None),
                "cnpj_mascara": cnpj_mascara,
                "cnpj": cnpj,
                "nome_pesquisa_sat": nome_pesquisa_sat,
                "operadora": operadora,
                "servico": servico,
                "filial": filial,
                "filtro": filtro,
                "mes_ano": p.mes_ano,
            }
        except Exception as e:
            logger.error(f"Erro ao processar item SAT {p.processo_id}: {e}")
            return None

    def return_process(self, processo_id: str, hash_execucao: str = ''):
        cnpj_mascara, cnpj, nome_pesquisa_sat, operadora, servico, filial, filtro, mes_ano = self.get_info_cadastro_coda(
            processo_id)
        prod = {
            "processo_id": processo_id,
            "hash_execucao": hash_execucao,
            "cnpj_mascara": cnpj_mascara,
            "cnpj": cnpj,
            "nome_pesquisa_sat": nome_pesquisa_sat,
            "operadora": operadora,
            "servico": servico,
            "filial": filial,
            "filtro": filtro,
            "mes_ano": mes_ano,
        }
        return prod

    def add_queue_item_sat(self, processo_id):
        try:
            processo = self.db.processo.read(
                {"processo_id": processo_id, "status_final": "COMPLETED"})
            if processo:
                fatura = processo.faturas[0]
                data_vencimento = fatura["data_vencimento"]
                caminho = fatura["caminho"]
                cadastro = self.db.cadastro.read(
                    {"hash_cron_cad": processo.hash_execucao})
                if cadastro:
                    operadora = cadastro.operadora

                    logger.info(
                        f"Item adicionado à fila com sucesso: {processo_id}")
                else:
                    logger.error(
                        f"Cadastro com hash {processo_id} não encontrado.")
                    return None
            else:
                logger.error(f"Processo com ID {processo_id} não encontrado.")
                return None
        except Exception as e:
            logger.error(f"Erro ao adicionar item à fila: {e}")
            return None

    def update_status_all(
        self,
        processo_id: str,
        session_id: str = "",
        status_execucao: StatusExecucao = StatusExecucao.FAILED,
        status_processo: StatusExecucao = StatusExecucao.FAILED,
        message: str = "",
    ):
        try:
            self.update_status_execucao(
                processo_id=processo_id,
                session_id=session_id,
                novo_status=status_execucao,
                detalhes=message,
            )
            self.update_status_processo(
                processo_id=processo_id, novo_status=status_processo, detalhes=message
            )
        except Exception as e:
            logger.critical(f"Erro crítico: {e}")

    # New method to update Coda in batch
    def update_coda_batch(self, rows_data):
        """Update Coda with multiple rows at once"""
        try:
            if not rows_data:
                return

            # Filter out None values
            valid_rows = [row for row in rows_data if row]

            if valid_rows:
                logger.info(
                    f"Enviando {len(valid_rows)} linhas para Coda em lote")
                add_rows_batch("DB-Cliente-Faturamento",
                               valid_rows, batch_size=10)
        except Exception as e:
            logger.error(f"Erro ao atualizar Coda em lote: {e}")
            # Fallback to individual updates
            for row in rows_data:
                if row:
                    try:
                        add_row("DB-Cliente-Faturamento", row)
                    except Exception as inner_e:
                        logger.error(f"Erro em fallback individual: {inner_e}")
