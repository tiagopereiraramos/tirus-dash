import os
from io import BytesIO

from configs.config import getenv
from minio import Minio
from minio.error import S3Error

# Configurações do MinIO
MINIO_ENDPOINT = getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = getenv("MINIO_SECRET_KEY")
BUCKET_NAME = getenv("BUCKET_NAME")

# Inicializar cliente do MinIO
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=True,  # Alterar para True se usar HTTPS
)


def upload_binary_to_minio(
    binary_data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
):
    """
    Faz upload de dados binários diretamente para o bucket do MinIO.

    :param binary_data: Dados binários a serem enviados
    :param object_name: Nome desejado para o arquivo no bucket
    :param content_type: Tipo do conteúdo (MIME type), padrão é "application/octet-stream"
    :return: Nome do objeto no bucket
    """
    try:
        print(f"Fazendo upload de dados binários para '{BUCKET_NAME}/{object_name}'...")

        # Usar BytesIO para criar um arquivo em memória a partir dos dados binários
        data_stream = BytesIO(binary_data)

        # Envia os dados binários para o MinIO
        client.put_object(
            bucket_name=BUCKET_NAME,
            object_name=object_name,
            data=data_stream,
            length=len(binary_data),
            content_type=content_type,
        )
        print(f"Upload de '{object_name}' concluído com sucesso.")
        return object_name
    except Exception as e:
        print(f"Erro ao fazer upload para o MinIO: {e}")
        raise


def upload_file_to_minio(file_path: str, object_name: str):
    """
    Faz upload de um arquivo local para o bucket do MinIO.

    :param file_path: Caminho do arquivo local
    :param object_name: Nome desejado para o arquivo no bucket
    """
    try:
        print(f"Fazendo upload de '{file_path}' para '{BUCKET_NAME}/{object_name}'...")
        client.fput_object(
            bucket_name=BUCKET_NAME,
            object_name=object_name,
            file_path=file_path,
        )
        print(f"Upload de '{file_path}' concluído com sucesso.")
        return f"{object_name}"
    except Exception as e:
        print(f"Erro ao fazer upload para o MinIO: {e}")


def download_file_from_minio(object_name: str, local_path: str):
    """
    Faz o download de um arquivo do bucket do MinIO para o disco local.

    :param object_name: Nome do arquivo no bucket
    :param local_path: Caminho local onde o arquivo será salvo temporariamente
    :return: Caminho do arquivo salvo localmente
    """
    try:
        print(f"Baixando '{object_name}' do bucket '{BUCKET_NAME}'...")
        client.fget_object(
            bucket_name=BUCKET_NAME,
            object_name=object_name,
            file_path=local_path,
        )
        print(f"Arquivo baixado para '{local_path}'.")
        return local_path
    except S3Error as e:
        print(f"Erro ao baixar arquivo do MinIO: {e}")
        return None


def delete_local_file(file_path: str):
    """
    Remove um arquivo do disco local.

    :param file_path: Caminho do arquivo local
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Arquivo '{file_path}' removido do disco local.")
        else:
            print(f"Arquivo '{file_path}' não encontrado no disco local.")
    except Exception as e:
        print(f"Erro ao deletar arquivo local: {e}")
