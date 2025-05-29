import hashlib
import importlib
import math
import os
import sys
import uuid
import threading
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Type
from bson import ObjectId

from util.mapeamento import get_hash, set_hash
from configs.config import getenv
from pymongo import MongoClient
from util.dataclass import (
    Cadastro,
    Log,
    LogLevel,
    WebhookPayload,
)


class Database:
    """
    Classe principal para manipular o banco de dados MongoDB,
    incluindo configurações dinâmicas de coleções e
    operações relacionadas a processos, faturas e logs.

    Thread-safe implementation with thread-local storage for connections.
    """

    # Class-level thread-local storage for connections
    _thread_local = threading.local()

    # Class-level connection pool to track and manage connections
    _connection_pool = set()
    _pool_lock = threading.RLock()

    # ---------- Inicialização e Configuração ----------

    def __init__(self):
        """Inicializa a conexão com o MongoDB e configura as coleções."""
        self.env = getenv("ENV", "prod").lower()
        self.uri = getenv("MONGO_URI", "mongodb://localhost:27017")
        self.database_name = (
            getenv("LOCAL_MONGO_DATABASE_DEV")
            if self.env == "dev"
            else getenv("LOCAL_MONGO_DATABASE_PROD")
        )
        self.is_dev = self.env == "dev"
        self.collections = self.load_collections_from_env()

        # Configura collections como propriedades dinâmicas
        # Agora elas serão acessadas através de property getters
        # que garantem acesso thread-safe
        for collection_name, dataclass_type in self.collections.items():
            setattr(
                self.__class__,
                collection_name,
                property(self._create_collection_property(
                    collection_name, dataclass_type))
            )

    def load_collections_from_env(self) -> Dict[str, Type]:
        """Carrega as coleções definidas na variável de ambiente COLLECTIONS."""
        collections_str = getenv("COLLECTIONS", "")
        collections = {}
        if collections_str:
            for item in collections_str.split(","):
                try:
                    collection_name, dataclass_name = item.split(":")
                    dataclass_module = importlib.import_module(
                        "util.dataclass"
                    )
                    dataclass_type = getattr(dataclass_module, dataclass_name)
                    collections[collection_name] = dataclass_type
                except (ValueError, ImportError, AttributeError) as e:
                    print(f"Erro ao carregar coleção: {item}. Detalhes: {e}")
        return collections

    # ---------- Thread-Safe Connection Management ----------

    @property
    def client(self):
        """Thread-safe access to MongoDB client"""
        if not hasattr(self._thread_local, 'client'):
            # Create a new connection for this thread
            self._thread_local.client = MongoClient(self.uri)

            # Track the connection for proper cleanup
            with self._pool_lock:
                self._connection_pool.add(self._thread_local.client)

        return self._thread_local.client

    @property
    def db(self):
        """Thread-safe access to database"""
        if not hasattr(self._thread_local, 'db'):
            self._thread_local.db = self.client[self.database_name]
        return self._thread_local.db

    def _create_collection_property(self, collection_name, dataclass_type):
        """Creates a property accessor function for a collection"""

        def get_collection_accessor(self):
            # Ensure thread-local storage has accessors dictionary
            if not hasattr(self._thread_local, 'collection_accessors'):
                self._thread_local.collection_accessors = {}

            # Create accessor if it doesn't exist for this thread
            if collection_name not in self._thread_local.collection_accessors:
                self._thread_local.collection_accessors[collection_name] = self._create_collection_accessor(
                    collection_name, dataclass_type
                )

            return self._thread_local.collection_accessors[collection_name]

        return get_collection_accessor

    # ---------- Auxiliares e Utilitários ----------

    def generate_hash_cad(self, nome_filtro: str, operadora: str, servico: str, dados_sat: str = "", filtro: str = "", unidade: str = "") -> str:
        """Gera um hash único para cada execução de um processo."""
        # Remover espaços nas variáveis e normalizar para minúsculas
        nome_filtro = nome_filtro.strip().lower()
        operadora = operadora.strip().lower()
        servico = servico.strip().lower()
        dados_sat = dados_sat.strip().lower() if dados_sat else ""
        filtro = filtro.strip().lower() if filtro else ""
        unidade = unidade.strip().lower() if unidade else ""

        # Gerar a string base para o hash
        base_string = f"{nome_filtro}-{operadora}-{servico}-{dados_sat}-{filtro}-{unidade}"
        # Gerar o hash
        hash_value = hashlib.sha256(base_string.encode()).hexdigest()[:16]

        return hash_value

    def generate_session_id(self, hash_cad: str) -> str:
        """Gera um session_id único para cada execução de um processo."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return hashlib.sha256(f"{hash_cad}-{timestamp}".encode()).hexdigest()[
            :16
        ]

    def generate_process_id(self, palavrachave: str = "TPSM") -> str:
        """Gera um identificador único para o processo."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_id = uuid.uuid4().hex  # UUID aleatório
        random_salt = str(uuid.uuid4())[
            :8
        ]  # Pegamos uma parte do UUID como salt

        raw_string = f"{palavrachave}-{timestamp}-{unique_id}-{random_salt}"
        return hashlib.sha256(raw_string.encode()).hexdigest()[:16]

    # ---------- Acesso e Operações CRUD ----------

    def _create_collection_accessor(
        self, collection_name: str, dataclass_type: Type
    ):
        """Cria uma classe para acessar coleções no MongoDB com operações CRUD."""

        class CollectionAccessor:
            def __init__(self, db, collection_name, dataclass_type):
                self.collection = db[collection_name]
                self.dataclass_type = dataclass_type

            @staticmethod
            def mongo_to_python(value: Any) -> Any:
                """Converte valores do MongoDB para tipos Python compatíveis."""
                if isinstance(value, dict) and "$date" in value:
                    # Converte timestamp MongoDB para datetime
                    return datetime.strptime(
                        value["$date"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                elif isinstance(value, ObjectId):
                    return str(value)
                elif isinstance(value, list):
                    # Converte listas recursivamente
                    return [
                        CollectionAccessor.mongo_to_python(v) for v in value
                    ]
                elif isinstance(value, dict):
                    # Converte dicionários recursivamente
                    return {
                        k: CollectionAccessor.mongo_to_python(v)
                        for k, v in value.items()
                    }
                return value

            @staticmethod
            def clean_field(value: Any) -> Optional[Any]:
                """Valida e limpa campos, convertendo enums e ignorando valores inválidos."""
                if value is None or (
                    isinstance(value, float) and math.isnan(value)
                ):
                    return None
                # Converte enums para seus valores
                if isinstance(value, Enum):
                    return value.value
                if isinstance(value, str):
                    return value
                return value

            def create(self, obj: Any) -> str:
                if not isinstance(obj, self.dataclass_type):
                    raise TypeError(
                        f"Expected instance of {self.dataclass_type}, got {type(obj)}"
                    )

                document = asdict(obj)

                # Limpar todos os campos dinamicamente
                for key, value in document.items():
                    document[key] = self.clean_field(value)

                if "_id" in document and document["_id"] is None:
                    del document["_id"]

                result = self.collection.insert_one(document)
                return str(result.inserted_id)

            def read(self, query: Dict) -> Any:
                """
                Lê os documentos de acordo com a consulta fornecida e converte para instâncias do dataclass.
                O _id será incluído como opcional nas instâncias.
                """
                documents = self.collection.find(query)
                instances = []

                for doc in documents:
                    # Converte todos os valores do MongoDB para Python
                    doc = self.mongo_to_python(doc)

                    # Instancia dinamicamente o dataclass
                    instance = self.dataclass_type(**doc)
                    instances.append(instance)

                # Retorna a primeira instância ou uma lista completa
                return instances[0] if len(instances) == 1 else instances

            def update(self, query: Dict, update_data: Dict) -> Optional[str]:
                """
                Atualiza um documento utilizando $set, ou um pipeline de agregação,
                dependendo do formato de update_data.
                Retorna o id do documento atualizado, ou None se não houver atualização.
                """
                try:
                    # Verifica se update_data tem a estrutura para um pipeline de agregação
                    if isinstance(update_data, list):
                        result = self.collection.update_one(query, update_data)
                    else:
                        result = self.collection.update_one(
                            query, {"$set": update_data}
                        )

                    # Verifica se o documento foi alterado
                    if result.matched_count > 0:
                        updated_doc = self.collection.find_one(query)
                        return str(updated_doc["_id"]) if updated_doc else None

                    return None  # Retorna None caso nenhum documento tenha sido alterado
                except Exception as e:
                    print(f"Error executing update: {e}")
                    return None

            def delete(self, query: Dict) -> int:
                result = self.collection.delete_one(query)
                return result.deleted_count

        return CollectionAccessor(self.db, collection_name, dataclass_type)

    # Adicione o caminho para encontrar os módulos de utilidade
    sys.path.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')))

    # ---------- Manipulação de Processos ----------

    def insert_cadastro(self, cadastro: Cadastro, linha_indice=None) -> str:
        # 1. Ignorar objetos vazios
        if not cadastro.to_dict():
            print("Objeto Cadastro vazio. Ignorado.")
            return ""

        try:
            # 2. Se as hashes forem iguais, nada mudou → não altera
            if cadastro.hash_auxiliar and cadastro.hash_cron_cad == cadastro.hash_auxiliar:
                print(
                    "Hash auxiliar e hash_cron_cad são iguais. Nenhuma alteração necessária.")
                return cadastro.hash_cron_cad

            # 3. Hash em branco na planilha - ATUALIZAR registro existente
            if not cadastro.hash_cron_cad and cadastro.hash_auxiliar:
                # Verificamos se temos a linha no mapeamento
                hash_antigo = get_hash(linha_indice)

                if hash_antigo:
                    print(
                        f"ENCONTRADO: Linha {linha_indice} tem hash antigo {hash_antigo}")

                    # Encontramos o hash antigo, vamos buscar o documento pelo hash
                    existing_document = self.cadastro.collection.find_one(
                        {"hash_cron_cad": hash_antigo})

                    if existing_document:
                        print(
                            f"ATUALIZANDO: Documento com hash {hash_antigo} para {cadastro.hash_auxiliar}")
                        # Atualiza hash no objeto cadastro
                        cadastro.hash_cron_cad = cadastro.hash_auxiliar

                        # Também atualiza no mapeamento
                        set_hash(
                            linha_indice, cadastro.hash_auxiliar)

                        # Chama o método de atualização de processos
                        self.atualiza_processos(
                            hash_antigo,
                            cadastro.hash_auxiliar,
                        )

                        # Prepara e executa a atualização
                        cadastro_dict = cadastro.to_dict()
                        if "_id" in cadastro_dict:
                            del cadastro_dict["_id"]

                        self.cadastro.update(
                            {"_id": existing_document["_id"]},
                            cadastro_dict,
                        )
                        print(f"SUCESSO: Documento atualizado com novos campos-chave")
                        return cadastro.hash_auxiliar
                    else:
                        print(
                            f"ATENÇÃO: Hash {hash_antigo} não encontrado no banco")

                # Se não encontramos o registro, criamos um novo
                print(f"CRIANDO NOVO: Hash em branco, sem registro existente")
                cadastro.hash_cron_cad = cadastro.hash_auxiliar
                self.cadastro.create(cadastro)

                # Atualiza o mapeamento
                if linha_indice:
                    set_hash(linha_indice, cadastro.hash_auxiliar)

                return cadastro.hash_cron_cad

            # 4. Se as hashes forem diferentes e ambas existirem → atualizar
            if cadastro.hash_auxiliar and cadastro.hash_cron_cad and cadastro.hash_cron_cad != cadastro.hash_auxiliar:
                existing_document = self.cadastro.collection.find_one(
                    {"hash_cron_cad": cadastro.hash_cron_cad}
                )
                if existing_document:
                    print(
                        f"Atualizando hash_cron_cad de {cadastro.hash_cron_cad} para {cadastro.hash_auxiliar}")
                    self.atualiza_processos(
                        cadastro.hash_cron_cad,
                        cadastro.hash_auxiliar,
                    )
                    cadastro.hash_cron_cad = cadastro.hash_auxiliar  # Atualiza no objeto

                    # Atualiza no mapeamento
                    if linha_indice:
                        set_hash(linha_indice, cadastro.hash_auxiliar)

                    cadastro_dict = cadastro.to_dict()
                    if "_id" in cadastro_dict:
                        del cadastro_dict["_id"]

                    self.cadastro.update(
                        {"_id": existing_document["_id"]},
                        cadastro_dict,
                    )
                    print(
                        f"Documento atualizado para: {cadastro.nome_filtro}, "
                        f"Operadora: {cadastro.operadora}, Serviço: {cadastro.servico}"
                    )
                    return cadastro.hash_cron_cad
                else:
                    print(
                        f"Hash antiga {cadastro.hash_cron_cad} não encontrada. Será tratado como novo registro.")
                    cadastro.hash_cron_cad = cadastro.hash_auxiliar
                    self.cadastro.create(cadastro)
                    return cadastro.hash_cron_cad

            # 5. Cenário anômalo
            print("Cadastro sem hash_cron_cad e sem hash_auxiliar. Ignorado.")
            return ""

        except Exception as e:
            print(f"Erro ao inserir ou atualizar dados no MongoDB: {e}")
            return "Erro"

    def insert_data_from_api(self, data: WebhookPayload):
        # Gerar hash_cron_cad e session_id para identificação única
        hash_cron_cad = self.generate_hash_cad(
            data.CNPJ,
            data.OPERADORA,
            data.SERVICO,
        )

        # Criando a instância de Cadastro se houver registro no banco
        cadastro = Cadastro(
            hash_cron_cad=hash_cron_cad,
            nome_filtro=data.NOME_FILTRO,
            cnpj_mascara=data.CNPJ,
            cnpj=data.CNPJ.replace(".", "").replace("/", "").replace("-", ""),
            operadora=data.OPERADORA,
            servico=data.SERVICO,
            filtro=data.FILIAL,
            unidade=data.FILIAL,
        )

        # Verificando se já existe um documento com o mesmo hash_cron
        existing_document = self.cadastro.collection.find_one(
            {"hash_cron_cad": hash_cron_cad}
        )
        try:
            if existing_document:
                # Garantir que o _id não seja passado durante a atualização
                cadastro_dict = asdict(cadastro)
                if "_id" in cadastro_dict:
                    del cadastro_dict["_id"]

                # Atualizar o documento existente
                self.cadastro.update(
                    {"_id": existing_document["_id"]},
                    cadastro_dict,
                )
                print(
                    f"Documento atualizado para CNPJ: {data.CNPJ}, Operadora: {cadastro.operadora}, Serviço: {cadastro.servico}"
                )
                return hash_cron_cad
            else:
                # Inserir um novo documento
                self.cadastro.create(cadastro)
                print(
                    f"Documento inserido para CNPJ: {data.CNPJ}, Operadora: {cadastro.operadora}, Serviço: {cadastro.servico}"
                )
                return hash_cron_cad
        except Exception as e:
            print(f"Erro ao inserir ou atualizar dados no MongoDB: {e}")
            return None

    def atualiza_processos(self, hash_cron_cad: str, hash_auxiliar: str):
        # Agora preciso verificar se existem processos vinculados a esse antigo hash_cron_cad
        # e atribuir os novos nos processos, A correta verificação é olhar se no mes_ano corrente existia a hash_execucao
        # com o valor da hash_cron_cad antigo e se existir, trocar pelo novo
        # Pegar o mes_ano corrente
        mes_ano_corrente = datetime.now().strftime("%Y-%m")
        processo = self.processo.read(
            {"hash_execucao": hash_cron_cad, "mes_ano": mes_ano_corrente})
        if processo:
            self.processo.update(
                {"_id": processo._id},
                {"hash_cron_cad": hash_auxiliar},
            )
            print(
                f"Processo atualizado de {hash_cron_cad} para {hash_auxiliar}"
            )
        else:
            print("Nenhum processo encontrado com o hash_cron_cad antigo.")

    # ---------- Logs e Monitoramento ----------

    def log_event(
        self,
        hash_cron_cad: str,
        session_id: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
    ):
        """Insere um evento de log na coleção de logs."""
        log_data = Log(
            hash_cron_cad=hash_cron_cad,
            session_id=session_id,
            level=level,
            message=message,
            time=datetime.now(),
        )
        self.log.create(asdict(log_data))

    # ---------- Encerramento ----------

    def close(self):
        """Fecha a conexão com o MongoDB para este thread."""
        if hasattr(self._thread_local, 'client'):
            self._thread_local.client.close()

            # Remove from pool
            with self._pool_lock:
                if self._thread_local.client in self._connection_pool:
                    self._connection_pool.remove(self._thread_local.client)

            # Clean up thread-local variables
            delattr(self._thread_local, 'client')
            if hasattr(self._thread_local, 'db'):
                delattr(self._thread_local, 'db')
            if hasattr(self._thread_local, 'collection_accessors'):
                delattr(self._thread_local, 'collection_accessors')

    @classmethod
    def close_all_connections(cls):
        """Close all MongoDB connections in the pool"""
        with cls._pool_lock:
            for client in list(cls._connection_pool):
                try:
                    client.close()
                except:
                    pass
            cls._connection_pool.clear()
