"""
Teste Individual - Azuton RPA
Permite testar o RPA da Azuton isoladamente sem orquestração
Conforme especificações do manual BGTELECOM
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.rpa.azuton_rpa import AzutonRPA
import logging

# Configuração de logging para debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_azuton_rpa_individual():
    """
    Teste individual do RPA Azuton
    Usa dados reais da BGTELECOM conforme manual
    """
    print("=== TESTE INDIVIDUAL AZUTON RPA ===")
    
    # Cliente real da BGTELECOM para teste
    cliente_teste = {
        'hash_unico': 'RICAL_AZUTON_INTERNET',
        'razao_social': 'RICAL LTDA',
        'nome_sat': 'RICAL INTERNET',
        'cnpj': '12.345.678/0001-90',
        'operadora_codigo': 'AZUTON',
        'filtro': 'INTERNET',
        'servico': 'BANDA_LARGA',
        'unidade': 'FILIAL_02',
        'site_emissao': 'https://portal.azuton.com.br',
        'login_portal': 'rical_azuton_user',
        'senha_portal': 'azuton_pass_2025',
        'cpf': '123.456.789-00'
    }
    
    try:
        # Inicializa RPA Azuton
        azuton_rpa = AzutonRPA()
        logger.info("RPA Azuton inicializado com sucesso")
        
        # Parâmetros de execução
        parametros = {
            'cliente_id': 'test_rical_azuton_005',
            'mes_ano': '2025-05',
            'diretorio_download': './downloads/azuton/',
            'tentativa_numero': 1,
            'debug_mode': True,
            'timeout_navegacao': 45
        }
        
        print(f"Cliente: {cliente_teste['razao_social']}")
        print(f"Operadora: {cliente_teste['operadora_codigo']}")
        print(f"Portal: {cliente_teste['site_emissao']}")
        print(f"Mês/Ano: {parametros['mes_ano']}")
        
        # Executa RPA com dados do cliente
        resultado = azuton_rpa.executar_download(
            cliente_data=cliente_teste,
            parametros=parametros
        )
        
        if resultado['sucesso']:
            print("\n✅ SUCESSO: RPA Azuton executado com êxito")
            print(f"Arquivo baixado: {resultado.get('arquivo_baixado', 'N/A')}")
            print(f"URL S3: {resultado.get('url_s3', 'N/A')}")
            print(f"Tempo execução: {resultado.get('tempo_execucao', 'N/A')}s")
        else:
            print("\n❌ ERRO: Falha na execução do RPA Azuton")
            print(f"Mensagem: {resultado.get('mensagem_erro', 'Erro desconhecido')}")
            
        # Log detalhado para debug
        print(f"\n📋 LOGS DE EXECUÇÃO:")
        print(resultado.get('logs_execucao', 'Sem logs disponíveis'))
        
    except Exception as e:
        logger.error(f"Erro no teste RPA Azuton: {str(e)}")
        print(f"\n💥 EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()

def test_azuton_validation():
    """Testa validação de dados do cliente Azuton"""
    print("\n=== TESTE VALIDAÇÃO AZUTON ===")
    
    azuton_rpa = AzutonRPA()
    
    # Dados válidos para teste
    cliente_valido = {
        'cnpj': '12.345.678/0001-90',
        'login_portal': 'usuario_azuton',
        'senha_portal': 'senha_azuton_valida',
        'operadora_codigo': 'AZUTON'
    }
    
    try:
        validacao = azuton_rpa.validar_configuracao(cliente_valido)
        if validacao['valido']:
            print("✅ SUCESSO: Dados válidos aceitos")
        else:
            print("❌ ERRO: Dados válidos rejeitados")
            print(f"Erros: {validacao.get('erros', [])}")
    except Exception as e:
        print(f"Erro na validação: {str(e)}")

if __name__ == "__main__":
    # Executa testes individuais
    test_azuton_rpa_individual()
    test_azuton_validation()
    
    print("\n" + "="*50)
    print("TESTE INDIVIDUAL AZUTON RPA CONCLUÍDO")
    print("Verifique os logs para detalhes da execução")