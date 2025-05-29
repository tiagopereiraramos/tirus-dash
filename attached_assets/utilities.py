import difflib
import hashlib
from http.client import HTTPException
import os
import re
import shutil
from datetime import datetime
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Union
from platformdirs import user_downloads_dir
import requests
from services.minios3_service import (
    download_file_from_minio,
    upload_binary_to_minio,
    upload_file_to_minio,
)


def obter_periodo():
    hoje = datetime.today()

    # Definir a data de início: dia 20 do mês passado
    primeiro_dia_mes_atual = hoje.replace(day=1)
    data_inicio = primeiro_dia_mes_atual - timedelta(
        days=1
    )  # Retrocede para o dia 20 do mês anterior

    # Definir a data de fim: dia 15 do mês atual
    data_fim = hoje.replace(day=30)

    return data_inicio.strftime("%Y/%m/%d"), data_fim.strftime("%Y/%m/%d")


def get_latest_file(
    extension: Optional[str] = None,
    prefix: Optional[str] = None,
    timeout: int = 90,
    interval: float = 1.0,
) -> Union[Optional[str], List[str]]:
    """
    Obtém arquivos de um diretório de download, filtra por extensão e prefixo no nome,
    move para uma pasta de destino e retorna o caminho dos arquivos movidos.

    - Se a extensão for '.log', retorna **uma lista** com todos os arquivos correspondentes.
    - Para outras extensões, retorna **apenas o arquivo mais recente**.

    :param target_folder: Pasta onde os arquivos estão localizados.
    :param extension: Extensão do arquivo desejado (ex: ".pdf").
    :param prefix: Prefixo opcional que o nome do arquivo deve começar (ex: "Boleto" ou "Fatura").
    :param timeout: Tempo máximo para aguardar o arquivo aparecer.
    :param interval: Intervalo entre as verificações.
    :return: Caminho do arquivo mais recente encontrado ou lista de arquivos se forem logs.
    """

    start_time = time.time()
    download_path = Path(f"{user_downloads_dir()}/TIRUS_DOWNLOADS")

    try:
        if extension and not extension.startswith("."):
            extension = f".{extension}"

        print(
            f"Procurando arquivos no diretório '{download_path}' com critérios: "
            f"extensão='{extension}', prefixo='{prefix}', timeout={timeout}s"
        )

        enviados_folder = Path(user_downloads_dir()) / \
            "TIRUS_DOWNLOADS" / "Enviados"
        enviados_folder.mkdir(parents=True, exist_ok=True)
        while time.time() - start_time < timeout:
            # Lista todos os arquivos no diretório
            files = [f for f in download_path.iterdir() if f.is_file()]

            # Filtra por extensão, se fornecida
            if extension:
                files = [f for f in files if f.suffix == extension]

            # Filtra por prefixo no nome, se fornecido
            if prefix:
                files = [f for f in files if f.stem.startswith(prefix)]

            # Se for '.log', retorna todos os arquivos encontrados e os move para "Enviados"
            if extension == ".log" and files:
                moved_files = []
                for file in files:
                    new_location = enviados_folder / file.name
                    shutil.move(str(file), str(new_location))
                    moved_files.append(str(new_location))
                return moved_files  # Retorna a lista de arquivos movidos

            # Para outras extensões, retorna apenas o mais recente
            if files:
                latest_file = max(files, key=lambda x: x.stat().st_mtime)
                # Retorna o caminho do arquivo mais recente
                return str(latest_file)

            time.sleep(interval)  # Aguarda antes de tentar novamente

        print(
            f"Nenhum arquivo foi encontrado no diretório '{download_path}' dentro do tempo limite de {timeout} segundos."
        )
        return None

    except Exception as e:
        print(f"Erro ao procurar arquivos no diretório '{download_path}': {e}")
        return None


@staticmethod
def contains_similar_substring(
    original_site: str, servico_banco: str, threshold: float = 0.7
) -> bool:
    """
    Verifica se alguma parte da menor string é semelhante à maior string.

    Parâmetros:
        original_site (str): Texto original vindo do site.
        servico_banco (str): Texto armazenado no banco.
        threshold (float): Limite mínimo de similaridade para considerar como correspondência.

    Retorno:
        bool: True se encontrar uma correspondência com similaridade ≥ threshold, senão False.
    """

    def preprocess_string(s: str) -> str:
        """Remove caracteres não numéricos para facilitar a comparação."""
        return re.sub(r"\D", "", s)

    def get_similarity(str1: str, str2: str) -> float:
        """Calcula a similaridade entre duas strings numéricas."""
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    # Limpeza das strings (removendo caracteres não numéricos)
    str1_clean = preprocess_string(original_site)
    str2_clean = preprocess_string(servico_banco)

    # Define qual string é maior e qual é menor
    if len(str1_clean) > len(str2_clean):
        big, small = str1_clean, str2_clean
    else:
        big, small = str2_clean, str1_clean

    # Percorre a string maior, pegando pedaços do tamanho da menor e comparando similaridade
    for i in range(len(big) - len(small) + 1):
        chunk = big[i: i + len(small)]
        similarity = get_similarity(chunk, small)
        if similarity >= threshold:
            return True  # Encontrou um trecho semelhante suficiente

    return False  # Nenhuma correspondência encontrada acima do threshold


@staticmethod
# Precisamos fazer o tratamento do arquivo, subir ele para o minio para aí criar a fatura
def fetch_and_upload_to_minio(
    url: str,
    file_name: str,
    content_type: str = "application/octet-stream",
):
    """
    Faz o download de um arquivo via HTTP GET e realiza o upload direto para o MinIO.

    :param url: URL do arquivo a ser baixado.
    :param object_name: Nome desejado para o arquivo no bucket do MinIO.
    :param content_type: Tipo MIME do conteúdo, padrão é "application/octet-stream".
    :return: Nome do objeto salvo no bucket.
    """
    try:
        # Faz o download do arquivo
        file_name = sanitize_filename(file_name)
        object_name = f"pdfs/{file_name}"
        print(f"Baixando arquivo da URL: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Verifica se o status HTTP é 200
        binary_data = response.content
        print(f"Arquivo baixado com sucesso ({len(binary_data)} bytes).")

        # Chama o método de upload
        return upload_binary_to_minio(binary_data, object_name, content_type)
    except Exception as e:
        print(f"Erro durante download ou upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro durante download ou upload: {str(e)}",
        )


@staticmethod
def get_download_directory():

    # Get the user's downloads directory (platform-independent)
    base_download_dir = user_downloads_dir()

    # Create an app-specific subdirectory (optional - replace "myapp" with your app name)
    download_dir = os.path.join(base_download_dir, "TIRUS_DOWNLOADS")

    # Create the directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    return download_dir


@staticmethod
def renomear_arquivo(novo_nome):
    # Usa a função para obter o diretório de download
    download_dir = get_download_directory()

    # Verifica se o diretório existe
    if not os.path.exists(download_dir):
        print(f"O diretório de download não existe: {download_dir}")
        return False

    # Captura os arquivos atuais no diretório de download
    arquivos_anteriores = set(os.listdir(download_dir))

    # Tempo máximo de espera em segundos
    tempo_maximo_espera = 60
    tempo_passado = 0
    intervalo_espera = 5

    # Espera até que um novo arquivo apareça ou o tempo máximo seja atingido
    while tempo_passado < tempo_maximo_espera:
        # Espera 5 segundos antes de verificar novamente
        time.sleep(intervalo_espera)
        tempo_passado += intervalo_espera

        arquivos_atualizados = set(os.listdir(download_dir))

        # Verifica se um novo arquivo foi adicionado
        novo_arquivo = arquivos_atualizados - arquivos_anteriores
        if novo_arquivo:  # Se houver novos arquivos
            break
    else:
        # Se o loop terminou sem encontrar um novo arquivo
        print("Nenhum novo arquivo encontrado dentro do tempo limite.")
        return False

    # Encontra o arquivo mais recente baixado
    arquivos_atualizados = list(arquivos_atualizados)
    arquivos_atualizados.sort(
        key=lambda x: os.path.getmtime(os.path.join(download_dir, x)),
        reverse=True,
    )
    arquivo_recente = arquivos_atualizados[0]

    # Verifica o caminho completo do arquivo
    caminho_antigo = os.path.join(download_dir, arquivo_recente)
    caminho_novo = os.path.join(download_dir, "renamed", novo_nome)

    # Renomeia o arquivo
    os.rename(caminho_antigo, caminho_novo)
    print(f"Arquivo renomeado para {caminho_novo}")
    return True  # Retorna True se o arquivo foi renomeado com sucesso


@staticmethod
def sanitize_filename(filename: str) -> str:
    """
    Remove ou substitui caracteres inválidos em um nome de arquivo, garantindo que
    somente a extensão contenha o ponto final.

    Args:
        filename (str): O nome do arquivo a ser sanitizado.

    Returns:
        str: Nome de arquivo sanitizado.
    """
    # Define uma expressão regular para caracteres inválidos
    invalid_chars_pattern = r'[<>:"/\\|?*]'

    # Divide o nome do arquivo em nome e extensão
    if "." in filename:
        name, extension = filename.rsplit(".", 1)
        extension = (
            f".{extension}" if len(extension) <= 4 else ""
        )  # Considera extensão válida
    else:
        name, extension = filename, ""

    # Substitui caracteres inválidos no nome
    sanitized_name = re.sub(invalid_chars_pattern, "_", name)

    # Substitui múltiplos espaços ou pontos no nome
    # Substitui espaços por '_'
    sanitized_name = re.sub(r"\s+", "_", sanitized_name)
    # Remove pontos no meio
    sanitized_name = re.sub(r"\.+", "_", sanitized_name)

    # Remove underscores no início ou fim
    sanitized_name = sanitized_name.strip("_")

    # Garante que o nome não seja vazio
    if not sanitized_name:
        sanitized_name = "arquivo_sanitizado"

    return sanitized_name + extension


@staticmethod
def get_files_from_s3(nome_arquivo: str) -> tuple[str, str]:
    """
    Faz download de um arquivo do bucket S3 e retorna o caminho local e o nome do arquivo.
    :param nome_arquivo: Nome do arquivo no bucket.
    :return: Caminho absoluto do arquivo baixado localmente e o nome do arquivo.
    """
    try:
        # Define o diretório base como 'app' diretamente
        base_dir = Path(__file__).resolve().parents[1]  # Diretório app
        download_dir = (
            base_dir / "downloads"
        )  # Diretório onde os arquivos de download são armazenados

        # Garante que o caminho do diretório exista
        download_dir.mkdir(parents=True, exist_ok=True)

        # Caminho local completo do arquivo
        local_temp_path = download_dir / nome_arquivo

        # Define o nome do arquivo sem o prefixo de diretório do bucket
        caminho_pasta = "pdfs/"
        file = nome_arquivo.replace(caminho_pasta, "")

        # Faz o download do arquivo do MinIO
        file_path = download_file_from_minio(
            nome_arquivo, str(local_temp_path))

        return file_path, file
    except Exception as e:
        print(f"Erro ao fazer download do arquivo do MinIO: {e}")
        raise


@staticmethod
def upload_file_to_s3(file_path: str, pasta=True) -> str:
    """
    Faz upload de um arquivo local para a pasta `pdfs/` no bucket S3.

    :param file_path: Nome do arquivo ou caminho. Se for apenas nome, será procurado em locais padrão.
    :param pasta: (mantido para compatibilidade)
    :return: Caminho completo do arquivo no bucket.
    """
    try:
        # Diretório de destino
        download_dir = Path(user_downloads_dir()) / "TIRUS_DOWNLOADS"
        download_dir.mkdir(parents=True, exist_ok=True)

        # Primeiro verifica se é apenas nome de arquivo ou caminho completo
        path_obj = Path(file_path)
        file_name = path_obj.name

        # Locais possíveis onde o arquivo pode estar
        possible_locations = [
            path_obj,                           # Caminho exato fornecido
            Path.cwd() / file_name,             # No diretório atual
            Path(user_downloads_dir()) / file_name,  # Na pasta Downloads
            download_dir / file_name            # Na pasta TIRUS_DOWNLOADS
        ]

        # Procura o arquivo nas possíveis localizações
        original_path = None
        for loc in possible_locations:
            if loc.is_file():
                original_path = loc
                break

        if not original_path:
            raise FileNotFoundError(
                f"Arquivo '{file_name}' não encontrado em nenhum local padrão")

        # Local de destino temporário antes do upload
        local_temp_path = download_dir / file_name

        # Só copia o arquivo se ele ainda não estiver no destino
        if original_path != local_temp_path:
            shutil.copy2(str(original_path), str(local_temp_path))
            print(f"Arquivo copiado de {original_path} para {local_temp_path}")

        # Caminho do objeto no bucket
        object_name = f"pdfs/{file_name}"

        # Faz o upload
        uploaded_file = upload_file_to_minio(str(local_temp_path), object_name)

        # Remove o arquivo local após upload
        local_temp_path.unlink()

        return uploaded_file

    except Exception as e:
        print(f"Erro ao fazer upload para o MinIO: {e}")
        raise


@staticmethod
def get_current_month_year() -> str:
    return datetime.today().strftime("%Y-%m")


@staticmethod
def generate_hash_cad(nome_filtro: str, operadora: str, servico: str, dados_sat: str, filtro: str, unidade: str) -> str:
    """Gera um hash único para cada execução de um processo."""
    # Remover espaços nas variáveis e normalizar para minúsculas
    nome_filtro = nome_filtro.strip().lower()
    operadora = operadora.strip().lower()
    servico = servico.strip().lower()
    dados_sat = dados_sat.strip().lower()
    filtro = filtro.strip().lower()
    unidade = unidade.strip().lower()

    # Gerar a string base para o hash
    base_string = f"{nome_filtro}-{operadora}-{servico}-{dados_sat}-{filtro}-{unidade}"
    # Gerar o hash
    hash_value = hashlib.sha256(base_string.encode()).hexdigest()[:16]

    return hash_value
