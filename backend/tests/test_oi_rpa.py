"""
Teste Individual - OI RPA
Permite testar o RPA da OI isoladamente sem orquestração
Conforme especificações do manual BGTELECOM
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.rpa.oi_rpa import OIRPA
import logging

# Configuração de logging para debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_oi_rpa_individual():
    """
    Teste individual do RPA OI
    Usa dados reais da BGTELECOM conforme manual
    """
    print("=== TESTE INDIVIDUAL OI RPA ===")
    
    # Cliente real da BGTELECOM para teste
    cliente_teste = {
        'hash_unico': 'ALVORADA_OI_EMPRESARIAL',
        'razao_social': 'ALVORADA TELECOMUNICACOES LTDA',
        'nome_sat': 'ALVORADA EMPRESARIAL',
        'cnpj': '23.456.789/0001-80',
        'operadora_codigo': 'OI',
        'filtro': 'EMPRESARIAL',
        'servico': 'TELEFONIA',
        'unidade': 'FILIAL_001',
        'site_emissao': 'https://empresarial.oi.com.br',
        'login_portal': 'alvorada_emp_user',
        'senha_portal': 'senha_oi_2025',
        'cpf': '234.567.890-11'
    }
    
    try:
        # Inicializa RPA OI
        oi_rpa = OIRPA()
        logger.info("RPA OI inicializado com sucesso")
        
        # Parâmetros de execução
        parametros = {
            'cliente_id': 'test_alvorada_002',
            'mes_ano': '2025-05',
            'diretorio_download': './downloads/oi/',
            'tentativa_numero': 1,
            'debug_mode': True,
            'timeout_navegacao': 60
        }
        
        print(f"Cliente: {cliente_teste['razao_social']}")
        print(f"Operadora: {cliente_teste['operadora_codigo']}")
        print(f"Portal: {cliente_teste['site_emissao']}")
        print(f"Mês/Ano: {parametros['mes_ano']}")
        
        # Executa RPA com dados do cliente
        resultado = oi_rpa.executar_download_fatura(
            cliente_data=cliente_teste,
            parametros=parametros
        )
        
        if resultado['sucesso']:
            print("\n✅ SUCESSO: RPA OI executado com êxito")
            print(f"Arquivo baixado: {resultado.get('arquivo_baixado', 'N/A')}")
            print(f"URL S3: {resultado.get('url_s3', 'N/A')}")
            print(f"Tempo execução: {resultado.get('tempo_execucao', 'N/A')}s")
        else:
            print("\n❌ ERRO: Falha na execução do RPA OI")
            print(f"Mensagem: {resultado.get('mensagem_erro', 'Erro desconhecido')}")
            
        # Log detalhado para debug
        print(f"\n📋 LOGS DE EXECUÇÃO:")
        print(resultado.get('logs_execucao', 'Sem logs disponíveis'))
        
    except Exception as e:
        logger.error(f"Erro no teste RPA OI: {str(e)}")
        print(f"\n💥 EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()

def test_oi_validation():
    """Testa validação de dados do cliente OI"""
    print("\n=== TESTE VALIDAÇÃO OI ===")
    
    oi_rpa = OIRPA()
    
    # Dados inválidos para teste
    cliente_invalido = {
        'cnpj': 'cnpj_invalido',
        'login_portal': '',
        'senha_portal': None
    }
    
    try:
        validacao = oi_rpa.validar_dados_cliente(cliente_invalido)
        if validacao['valido']:
            print("❌ ERRO: Validação deveria ter falhado")
        else:
            print("✅ SUCESSO: Validação funcionando corretamente")
            print(f"Erros encontrados: {validacao['erros']}")
    except Exception as e:
        print(f"Erro na validação: {str(e)}")

if __name__ == "__main__":
    # Executa testes individuais
    test_oi_rpa_individual()
    test_oi_validation()
    
    print("\n" + "="*50)
    print("TESTE INDIVIDUAL OI RPA CONCLUÍDO")
    print("Verifique os logs para detalhes da execução")