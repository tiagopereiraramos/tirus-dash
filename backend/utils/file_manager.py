"""
Gerenciador de arquivos
Integração com MinIO/S3 e gerenciamento de downloads
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class FileManager:
    """Gerenciador de arquivos para o sistema RPA"""
    
    def __init__(self):
        self.download_dir = self._setup_download_directory()
        self.temp_dir = self._setup_temp_directory()
    
    def _setup_download_directory(self) -> str:
        """Configura diretório de downloads"""
        downloads_path = Path.home() / "Downloads" / "RPA_DOWNLOADS"
        downloads_path.mkdir(parents=True, exist_ok=True)
        return str(downloads_path)
    
    def _setup_temp_directory(self) -> str:
        """Configura diretório temporário"""
        temp_path = Path.home() / "temp" / "rpa_temp"
        temp_path.mkdir(parents=True, exist_ok=True)
        return str(temp_path)
    
    def get_download_dir(self) -> str:
        """Retorna diretório de downloads"""
        return self.download_dir
    
    def listar_arquivos_download(self) -> List[str]:
        """Lista arquivos no diretório de download"""
        try:
            return [f for f in os.listdir(self.download_dir) 
                   if os.path.isfile(os.path.join(self.download_dir, f))]
        except OSError:
            return []
    
    def renomear_arquivo(self, arquivo_origem: str, novo_nome: str) -> str:
        """Renomeia arquivo e retorna caminho completo"""
        try:
            # Se arquivo_origem é apenas nome, assumir que está no download_dir
            if not os.path.dirname(arquivo_origem):
                arquivo_origem = os.path.join(self.download_dir, arquivo_origem)
            
            caminho_destino = os.path.join(self.download_dir, novo_nome)
            shutil.move(arquivo_origem, caminho_destino)
            return caminho_destino
        except Exception as e:
            raise Exception(f"Erro ao renomear arquivo: {e}")
    
    def upload_to_s3(self, arquivo_local: str, cliente_hash: str, mes_ano: str) -> str:
        """
        Simula upload para S3/MinIO
        Em produção, conectaria com o serviço real
        """
        try:
            # Gerar URL simulada para S3
            nome_arquivo = os.path.basename(arquivo_local)
            s3_key = f"faturas/{cliente_hash}/{mes_ano}/{nome_arquivo}"
            s3_url = f"https://bucket-name.s3.amazonaws.com/{s3_key}"
            
            # Em ambiente de produção, aqui faria o upload real:
            # self._upload_real_s3(arquivo_local, s3_key)
            
            return s3_url
        except Exception as e:
            raise Exception(f"Erro no upload S3: {e}")
    
    def validar_arquivo_pdf(self, caminho_arquivo: str) -> bool:
        """Valida se arquivo é PDF válido"""
        try:
            if not os.path.exists(caminho_arquivo):
                return False
            
            # Verificar extensão
            if not caminho_arquivo.lower().endswith('.pdf'):
                return False
            
            # Verificar tamanho mínimo
            if os.path.getsize(caminho_arquivo) < 1024:  # 1KB mínimo
                return False
            
            # Verificar header PDF
            with open(caminho_arquivo, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False
            
            return True
        except Exception:
            return False
    
    def limpar_downloads_antigos(self, dias: int = 7):
        """Remove downloads antigos"""
        try:
            agora = datetime.now()
            for arquivo in os.listdir(self.download_dir):
                caminho_arquivo = os.path.join(self.download_dir, arquivo)
                if os.path.isfile(caminho_arquivo):
                    modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                    if (agora - modificacao).days > dias:
                        os.remove(caminho_arquivo)
        except Exception as e:
            print(f"Erro ao limpar downloads antigos: {e}")
    
    def obter_info_arquivo(self, caminho_arquivo: str) -> dict:
        """Obtém informações do arquivo"""
        try:
            stat = os.stat(caminho_arquivo)
            return {
                "nome": os.path.basename(caminho_arquivo),
                "tamanho": stat.st_size,
                "modificado": datetime.fromtimestamp(stat.st_mtime),
                "extensao": os.path.splitext(caminho_arquivo)[1],
                "existe": True
            }
        except Exception:
            return {"existe": False}