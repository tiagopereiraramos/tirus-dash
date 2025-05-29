"""
Serviço de Geração de Hash
Sistema RPA BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
"""

import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def generate_hash_cad(
    nome_filtro: str, 
    operadora: str, 
    servico: str, 
    dados_sat: str = "", 
    filtro: str = "", 
    unidade: str = ""
) -> str:
    """
    Gera hash único para identificação do cliente/processo
    Conforme especificação do manual BGTELECOM
    """
    try:
        # Normalizar strings
        nome_filtro = (nome_filtro or "").strip().upper()
        operadora = (operadora or "").strip().upper()
        servico = (servico or "").strip().upper()
        dados_sat = (dados_sat or "").strip().upper()
        filtro = (filtro or "").strip().upper()
        unidade = (unidade or "").strip().upper()
        
        # Concatenar componentes na ordem específica
        componentes = [
            nome_filtro,
            operadora,
            servico,
            dados_sat,
            filtro,
            unidade
        ]
        
        # Criar string única
        string_unica = "|".join(componentes)
        
        # Gerar hash SHA256
        hash_objeto = hashlib.sha256(string_unica.encode('utf-8'))
        hash_hex = hash_objeto.hexdigest()
        
        # Retornar os primeiros 32 caracteres
        hash_final = hash_hex[:32].upper()
        
        logger.debug(f"Hash gerado: {hash_final} para componentes: {string_unica}")
        
        return hash_final
        
    except Exception as e:
        logger.error(f"Erro ao gerar hash: {str(e)}")
        # Fallback hash baseado apenas no nome e operadora
        fallback_string = f"{nome_filtro}|{operadora}"
        fallback_hash = hashlib.md5(fallback_string.encode('utf-8')).hexdigest()[:16].upper()
        logger.warning(f"Usando hash fallback: {fallback_hash}")
        return fallback_hash

def validar_hash_unico(hash_value: str) -> bool:
    """Valida se o hash tem formato correto"""
    try:
        if not hash_value:
            return False
        
        # Deve ter exatamente 32 caracteres hexadecimais
        if len(hash_value) != 32:
            return False
        
        # Deve ser hexadecimal válido
        int(hash_value, 16)
        
        return True
        
    except (ValueError, TypeError):
        return False