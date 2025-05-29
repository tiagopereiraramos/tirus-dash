"""
Teste Individual - Vivo RPA
Permite testar o RPA da Vivo isoladamente sem orquestração
Conforme especificações do manual BGTELECOM
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.rpa.vivo_rpa import VivoRPA
from backend.models.cliente import Cliente
import logging

# Configuração de logging para debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vivo_rpa_individual():
    """
    Teste individual do RPA Vivo
    Usa dados reais da BGTELECOM conforme manual
    """
    print("=== TESTE INDIVIDUAL VIVO RPA ===")
    
    # Cliente real da BGTELECOM para teste
    cliente_teste = {
        'hash_unico': 'RICAL_VIVO_CORPORATIVO',
        'razao_social': 'RICAL LTDA',
        'nome_sat': 'RICAL CORPORATIVO',
        'cnpj': '12.345.678/0001-90',
        'operadora_codigo': 'VIVO',
        'filtro': 'CORPORATIVO',
        'servico': 'DADOS',
        'unidade': 'MATRIZ',
        'site_emissao': 'https://meuvivo.vivo.com.br',
        'login_portal': 'rical_corp_user',
        'senha_portal': 'senha_segura_123',
        'cpf': '123.456.789-00'
    }
    
    try:
        # Inicializa RPA Vivo
        vivo_rpa = VivoRPA()
        logger.info("RPA Vivo inicializado com sucesso")
        
        # Parâmetros de execução
        parametros = {
            'cliente_id': 'test_rical_001',
            'mes_ano': '2025-05',
            'diretorio_download': './downloads/vivo/',
            'tentativa_numero': 1,
            'debug_mode': True
        }
        
        print(f"Cliente: {cliente_teste['razao_social']}")
        print(f"Operadora: {cliente_teste['operadora_codigo']}")
        print(f"Portal: {cliente_teste['site_emissao']}")
        print(f"Mês/Ano: {parametros['mes_ano']}")
        
        # Executa RPA com dados do cliente
        resultado = vivo_rpa.executar_download_fatura(
            cliente_data=cliente_teste,
            parametros=parametros
        )
        
        if resultado['sucesso']:
            print("\n✅ SUCESSO: RPA Vivo executado com êxito")
            print(f"Arquivo baixado: {resultado.get('arquivo_baixado', 'N/A')}")
            print(f"URL S3: {resultado.get('url_s3', 'N/A')}")
            print(f"Tempo execução: {resultado.get('tempo_execucao', 'N/A')}s")
        else:
            print("\n❌ ERRO: Falha na execução do RPA Vivo")
            print(f"Mensagem: {resultado.get('mensagem_erro', 'Erro desconhecido')}")
            
        # Log detalhado para debug
        print(f"\n📋 LOGS DE EXECUÇÃO:")
        print(resultado.get('logs_execucao', 'Sem logs disponíveis'))
        
    except Exception as e:
        logger.error(f"Erro no teste RPA Vivo: {str(e)}")
        print(f"\n💥 EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()

def test_vivo_validation():
    """Testa validação de dados do cliente Vivo"""
    print("\n=== TESTE VALIDAÇÃO VIVO ===")
    
    vivo_rpa = VivoRPA()
    
    # Dados inválidos para teste
    cliente_invalido = {
        'cnpj': '',  # CNPJ vazio
        'login_portal': '',  # Login vazio
    }
    
    try:
        validacao = vivo_rpa.validar_dados_cliente(cliente_invalido)
        if validacao['valido']:
            print("❌ ERRO: Validação deveria ter falhado")
        else:
            print("✅ SUCESSO: Validação funcionando corretamente")
            print(f"Erros encontrados: {validacao['erros']}")
    except Exception as e:
        print(f"Erro na validação: {str(e)}")

if __name__ == "__main__":
    # Executa testes individuais
    test_vivo_rpa_individual()
    test_vivo_validation()
    
    print("\n" + "="*50)
    print("TESTE INDIVIDUAL VIVO RPA CONCLUÍDO")
    print("Verifique os logs para detalhes da execução")