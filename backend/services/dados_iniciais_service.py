"""
Sistema de Inicialização com Dados Reais da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

import logging
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from ..models.operadora import Operadora
from ..models.cliente import Cliente

logger = logging.getLogger(__name__)

class DadosIniciaisService:
    """Serviço para inicialização com dados reais da BGTELECOM"""
    
    def __init__(self):
        logger.info("Serviço de dados iniciais carregado")
    
    def inicializar_sistema_completo(self, db: Session) -> Dict[str, Any]:
        """Inicializa sistema completo com dados reais"""
        try:
            # Criar operadoras
            resultado_operadoras = self._criar_operadoras(db)
            
            # Criar clientes reais
            resultado_clientes = self._criar_clientes_reais(db)
            
            # Criar processos iniciais
            resultado_processos = self._criar_processos_iniciais(db)
            
            return {
                "sucesso": True,
                "operadoras": resultado_operadoras,
                "clientes": resultado_clientes,
                "processos": resultado_processos,
                "mensagem": "Sistema inicializado com dados reais da BGTELECOM"
            }
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            db.rollback()
            return {"sucesso": False, "erro": str(e)}
    
    def _criar_operadoras(self, db: Session) -> Dict[str, Any]:
        """Cria operadoras conforme manual"""
        operadoras = [
            {
                "nome": "EMBRATEL",
                "codigo": "EMBRATEL",
                "possui_rpa": True,
                "url_portal": "https://webebt01.embratel.com.br/embratelonline/index.asp",
                "classe_rpa": "EmbratelRPA"
            },
            {
                "nome": "DIGITALNET", 
                "codigo": "DIGITALNET",
                "possui_rpa": True,
                "url_portal": "https://sac.digitalnetms.com.br/login",
                "classe_rpa": "DigitalnetRPA"
            },
            {
                "nome": "VIVO",
                "codigo": "VIVO", 
                "possui_rpa": True,
                "url_portal": "https://vivo.com.br",
                "classe_rpa": "VivoRPA"
            },
            {
                "nome": "OI",
                "codigo": "OI",
                "possui_rpa": True, 
                "url_portal": "https://oi.com.br",
                "classe_rpa": "OiRPA"
            },
            {
                "nome": "AZUTON",
                "codigo": "AZUTON",
                "possui_rpa": True,
                "url_portal": "https://azuton.com.br", 
                "classe_rpa": "AzutonRPA"
            },
            {
                "nome": "SAT",
                "codigo": "SAT",
                "possui_rpa": True,
                "url_portal": "",
                "classe_rpa": "SatRPA"
            }
        ]
        
        criadas = 0
        existentes = 0
        
        for op_data in operadoras:
            existente = db.query(Operadora).filter(Operadora.codigo == op_data["codigo"]).first()
            
            if not existente:
                operadora = Operadora(
                    id=str(uuid.uuid4()),
                    nome=op_data["nome"],
                    codigo=op_data["codigo"],
                    possui_rpa=op_data["possui_rpa"],
                    url_portal=op_data["url_portal"],
                    classe_rpa=op_data["classe_rpa"],
                    status_ativo=True,
                    configuracao_rpa={},
                    data_criacao=datetime.now(),
                    data_atualizacao=datetime.now()
                )
                db.add(operadora)
                criadas += 1
            else:
                existentes += 1
        
        db.commit()
        return {"criadas": criadas, "existentes": existentes}
    
    def _criar_clientes_reais(self, db: Session) -> Dict[str, Any]:
        """Cria clientes com dados reais da BGTELECOM"""
        
        # Mapear operadoras
        operadoras_map = {}
        operadoras = db.query(Operadora).all()
        for op in operadoras:
            operadoras_map[op.codigo] = op.id
        
        # Dados reais extraídos do CSV da BGTELECOM
        clientes_reais = [
            {
                "hash_unico": "f31949d0b3615a3a",
                "razao_social": "RICAL - RACK INDUSTRIA E COMERCIO DE ARROZ LTDA",
                "nome_sat": "RICAL - RACK INDUSTRIA E COMERCIO DE ARROZ LTDA", 
                "cnpj": "84.718.741/0001-00",
                "operadora": "EMBRATEL",
                "filtro": "00052488515-0000_25",
                "servico": "69 3411-6000",
                "dados_sat": "Fixo",
                "unidade": "Ji-Paraná-RO",
                "login_portal": "EOL7010309",
                "senha_portal": "bgtele005",
                "observacoes": "Baixar boleto, fatura detalhada e nf."
            },
            {
                "hash_unico": "6cdc16271b11d9b7",
                "razao_social": "RICAL - RACK INDUSTRIA E COMERCIO DE ARROZ LTDA",
                "nome_sat": "RICAL - RACK INDUSTRIA E COMERCIO DE ARROZ LTDA",
                "cnpj": "84.718.741/0001-00", 
                "operadora": "EMBRATEL",
                "filtro": "00052488515-0000_24",
                "servico": "JIP/IP/00438",
                "dados_sat": "Link Dedicado",
                "unidade": "Ji-Paraná-RO",
                "login_portal": "EOL7010309",
                "senha_portal": "bgtele005",
                "observacoes": "Baixar boleto, fatura detalhada e nf."
            },
            {
                "hash_unico": "da96da90fc5c9fc7", 
                "razao_social": "ALVORADA COMERCIO DE PRODUTOS AGROPECUÁRIOS LTDA",
                "nome_sat": "ALVORADA COMERCIO DE PRODUTOS AGROPECUÁRIOS LTDA",
                "cnpj": "01.963.040/0003-63",
                "operadora": "EMBRATEL",
                "filtro": "00008160481-0004",
                "servico": "Dados CPE.IP.02088",
                "dados_sat": "Link Dedicado", 
                "unidade": "Campo Grande-MS",
                "login_portal": "EOL4539758",
                "senha_portal": "bg30432979",
                "observacoes": "Baixar boleto, fatura detalhada e nf."
            },
            {
                "hash_unico": "5646ef3a1655e3da",
                "razao_social": "CENZE TRANSPORTES E COMERCIO DE COMBUSTÍVEIS",
                "nome_sat": "CENZE TRANSPORTES E COMERCIO DE COMBUSTÍVEIS",
                "cnpj": "15.447.568/0002-03",
                "operadora": "EMBRATEL",
                "filtro": "00008053421-0003",
                "servico": "Voz originado",
                "dados_sat": "Fixo",
                "unidade": "Campo Grande-MS",
                "login_portal": "EOL9190790",
                "senha_portal": "bgtele02",
                "observacoes": "Baixar boleto, fatura detalhada e nf."
            },
            {
                "hash_unico": "8ead2c8449ccdd3f",
                "razao_social": "FINANCIAL CONSTRUTORA INDUSTRIAL LTDA",
                "nome_sat": "FINANCIAL CONSTRUTORA INDUSTRIAL LTDA",
                "cnpj": "15.565.179/0001-00",
                "operadora": "EMBRATEL",
                "filtro": "00008660126-0001_24",
                "servico": "Voz originado",
                "dados_sat": "Fixo",
                "unidade": "Campo Grande-MS",
                "login_portal": "EOL8035089",
                "senha_portal": "bg30432979",
                "observacoes": "Baixar boleto, fatura detalhada e nf."
            },
            {
                "hash_unico": "5664837335b069bc",
                "razao_social": "SANTA IZABEL TRANSPORTE REVENDEDOR RETALHISTA LTDA",
                "nome_sat": "TRANSPORTADORA SANTA IZABEL LTDA",
                "cnpj": "00.411.566/0001-06",
                "operadora": "DIGITALNET",
                "filtro": "HAWJUOGYJF",
                "servico": "Link Dedicado",
                "dados_sat": "Link Dedicado",
                "unidade": "Link Dedicado",
                "login_portal": "00.411.566/0001-06",
                "senha_portal": "00411566000106",
                "observacoes": "Baixar bol e nf (senha para abrir pdf, 004)"
            },
            {
                "hash_unico": "6d93af1703a192bb",
                "razao_social": "CG SOLURB SOLUÇÕES AMBIENTAIS SPE LTDA",
                "nome_sat": "CG SOLURB SOLUÇÕES AMBIENTAIS SPE LTDA", 
                "cnpj": "17.064.901/0001-40",
                "operadora": "DIGITALNET",
                "filtro": "JIYJRQO7JJ",
                "servico": "Internet",
                "dados_sat": "Internet",
                "unidade": "Ecoponto GALPÃO - Senador",
                "login_portal": "17.064.901/0001-40",
                "senha_portal": "170640",
                "observacoes": "Baixar o bol e nf. (senha para abrir pdf, 170)"
            },
            {
                "hash_unico": "360ed0dd0bbaca2e",
                "razao_social": "ALVORADA COMERCIO DE PRODUTOS AGROPECUÁRIOS LTDA",
                "nome_sat": "ALVORADA COMERCIO DE PRODUTOS AGROPECUÁRIOS LTDA",
                "cnpj": "01.963.040/0003-63",
                "operadora": "DIGITALNET", 
                "filtro": "TUYJRQVVYY",
                "servico": "Internet",
                "dados_sat": "Internet",
                "unidade": "Campo Grande -MS - Jornalista Ben.",
                "login_portal": "01.963.040/0003-62",
                "senha_portal": "019633",
                "observacoes": "Baixar o bol e nf. (senha para abrir pdf, 019)"
            }
        ]
        
        criados = 0
        existentes = 0
        erros = 0
        
        for cliente_data in clientes_reais:
            try:
                # Verificar se já existe
                existente = db.query(Cliente).filter(
                    Cliente.hash_unico == cliente_data["hash_unico"]
                ).first()
                
                if existente:
                    existentes += 1
                    continue
                
                operadora_codigo = cliente_data["operadora"]
                if operadora_codigo not in operadoras_map:
                    erros += 1
                    continue
                
                cliente = Cliente(
                    id=str(uuid.uuid4()),
                    hash_unico=cliente_data["hash_unico"],
                    razao_social=cliente_data["razao_social"],
                    nome_sat=cliente_data["nome_sat"],
                    cnpj=cliente_data["cnpj"],
                    operadora_id=operadoras_map[operadora_codigo],
                    filtro=cliente_data["filtro"],
                    servico=cliente_data["servico"],
                    dados_sat=cliente_data["dados_sat"],
                    unidade=cliente_data["unidade"],
                    login_portal=cliente_data["login_portal"],
                    senha_portal=cliente_data["senha_portal"],
                    observacoes=cliente_data["observacoes"],
                    status="ativo",
                    data_criacao=datetime.now(),
                    data_atualizacao=datetime.now()
                )
                
                db.add(cliente)
                criados += 1
                
            except Exception as e:
                logger.error(f"Erro ao criar cliente: {e}")
                erros += 1
        
        db.commit()
        return {"criados": criados, "existentes": existentes, "erros": erros}
    
    def _criar_processos_iniciais(self, db: Session) -> Dict[str, Any]:
        """Cria processos iniciais para o mês atual"""
        try:
            from ..main import Processo, StatusProcesso
            
            mes_atual = datetime.now().strftime("%Y-%m")
            clientes = db.query(Cliente).filter(Cliente.status == "ativo").all()
            
            criados = 0
            existentes = 0
            
            for cliente in clientes:
                existente = db.query(Processo).filter(
                    Processo.cliente_id == cliente.id,
                    Processo.mes_ano == mes_atual
                ).first()
                
                if not existente:
                    processo = Processo(
                        id=f"{cliente.hash_unico}_{mes_atual}",
                        cliente_id=cliente.id,
                        mes_ano=mes_atual,
                        status_processo=StatusProcesso.AGUARDANDO_DOWNLOAD.value,
                        criado_automaticamente=True,
                        data_criacao=datetime.now()
                    )
                    db.add(processo)
                    criados += 1
                else:
                    existentes += 1
            
            db.commit()
            return {"criados": criados, "existentes": existentes}
            
        except Exception as e:
            logger.error(f"Erro ao criar processos: {e}")
            return {"criados": 0, "existentes": 0, "erro": str(e)}

# Instância global
dados_iniciais_service = DadosIniciaisService()