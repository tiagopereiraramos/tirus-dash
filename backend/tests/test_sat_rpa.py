"""
Teste Individual - SAT RPA
Permite testar o RPA do SAT isoladamente sem orquestração
Conforme especificações do manual BGTELECOM
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.rpa.sat_rpa import SATRPA
import logging

# Configuração de logging para debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sat_rpa_individual():
    """
    Teste individual do RPA SAT
    Usa dados reais da BGTELECOM conforme manual
    """
    print("=== TESTE INDIVIDUAL SAT RPA ===")
    
    # Cliente real da BGTELECOM para teste
    cliente_teste = {
        'hash_unico': 'FINANCIAL_SAT_UPLOAD',
        'razao_social': 'FINANCIAL SERVICES LTDA',
        'nome_sat': 'FINANCIAL SAT',
        'cnpj': '45.678.901/0001-60',
        'operadora_codigo': 'SAT',
        'filtro': 'UPLOAD_SISTEMA',
        'servico': 'GESTAO_FINANCEIRA',
        'unidade': 'CONTROLADORIA',
        'site_emissao': 'https://sat.sistema.com.br',
        'login_portal': 'financial_sat_user',
        'senha_portal': 'sat_secure_2025',
        'dados_sat': 'sistema_financeiro_principal'
    }
    
    try:
        # Inicializa RPA SAT
        sat_rpa = SATRPA()
        logger.info("RPA SAT inicializado com sucesso")
        
        # Parâmetros de execução
        parametros = {
            'cliente_id': 'test_financial_004',
            'mes_ano': '2025-05',
            'arquivo_fatura': './downloads/test_fatura.pdf',
            'tentativa_numero': 1,
            'debug_mode': True,
            'timeout_upload': 120,
            'validar_upload': True
        }
        
        print(f"Cliente: {cliente_teste['razao_social']}")
        print(f"Sistema: {cliente_teste['operadora_codigo']}")
        print(f"Portal: {cliente_teste['site_emissao']}")
        print(f"Arquivo: {parametros['arquivo_fatura']}")
        
        # Executa RPA com dados do cliente
        resultado = sat_rpa.executar_upload_sat(
            cliente_data=cliente_teste,
            parametros=parametros
        )
        
        if resultado['sucesso']:
            print("\n✅ SUCESSO: RPA SAT executado com êxito")
            print(f"Upload realizado: {resultado.get('upload_confirmado', 'N/A')}")
            print(f"ID Transação: {resultado.get('id_transacao', 'N/A')}")
            print(f"Tempo execução: {resultado.get('tempo_execucao', 'N/A')}s")
        else:
            print("\n❌ ERRO: Falha na execução do RPA SAT")
            print(f"Mensagem: {resultado.get('mensagem_erro', 'Erro desconhecido')}")
            
        # Log detalhado para debug
        print(f"\n📋 LOGS DE EXECUÇÃO:")
        print(resultado.get('logs_execucao', 'Sem logs disponíveis'))
        
    except Exception as e:
        logger.error(f"Erro no teste RPA SAT: {str(e)}")
        print(f"\n💥 EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()

def test_sat_validation():
    """Testa validação de dados do cliente SAT"""
    print("\n=== TESTE VALIDAÇÃO SAT ===")
    
    sat_rpa = SATRPA()
    
    # Dados válidos para teste
    cliente_valido = {
        'cnpj': '45.678.901/0001-60',
        'dados_sat': 'sistema_principal',
        'login_portal': 'usuario_sat',
        'senha_portal': 'senha_sat_valida'
    }
    
    try:
        validacao = sat_rpa.validar_configuracao(cliente_valido)
        if validacao['valido']:
            print("✅ SUCESSO: Dados válidos aceitos")
        else:
            print("❌ ERRO: Dados válidos rejeitados")
            print(f"Erros: {validacao.get('erros', [])}")
    except Exception as e:
        print(f"Erro na validação: {str(e)}")

if __name__ == "__main__":
    # Executa testes individuais
    test_sat_rpa_individual()
    test_sat_validation()
    
    print("\n" + "="*50)
    print("TESTE INDIVIDUAL SAT RPA CONCLUÍDO")
    print("Verifique os logs para detalhes da execução")