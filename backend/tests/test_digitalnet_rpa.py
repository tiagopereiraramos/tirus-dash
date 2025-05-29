"""
Teste Individual - DigitalNet RPA
Permite testar o RPA da DigitalNet isoladamente sem orquestração
Conforme especificações do manual BGTELECOM
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.rpa.digitalnet_rpa import DigitalNetRPA
import logging

# Configuração de logging para debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_digitalnet_rpa_individual():
    """
    Teste individual do RPA DigitalNet
    Usa dados reais da BGTELECOM conforme manual
    """
    print("=== TESTE INDIVIDUAL DIGITALNET RPA ===")
    
    # Cliente real da BGTELECOM para teste
    cliente_teste = {
        'hash_unico': 'ALVORADA_DIGITALNET_FIBRA',
        'razao_social': 'ALVORADA TELECOMUNICACOES LTDA',
        'nome_sat': 'ALVORADA FIBRA',
        'cnpj': '23.456.789/0001-80',
        'operadora_codigo': 'DIGITALNET',
        'filtro': 'FIBRA_OPTICA',
        'servico': 'INTERNET_FIBRA',
        'unidade': 'SEDE_PRINCIPAL',
        'site_emissao': 'https://cliente.digitalnet.com.br',
        'login_portal': 'alvorada_digitalnet_user',
        'senha_portal': 'digitalnet_2025_pass',
        'cpf': '234.567.890-11'
    }
    
    try:
        # Inicializa RPA DigitalNet
        digitalnet_rpa = DigitalNetRPA()
        logger.info("RPA DigitalNet inicializado com sucesso")
        
        # Parâmetros de execução
        parametros = {
            'cliente_id': 'test_alvorada_digitalnet_006',
            'mes_ano': '2025-05',
            'diretorio_download': './downloads/digitalnet/',
            'tentativa_numero': 1,
            'debug_mode': True,
            'timeout_navegacao': 60
        }
        
        print(f"Cliente: {cliente_teste['razao_social']}")
        print(f"Operadora: {cliente_teste['operadora_codigo']}")
        print(f"Portal: {cliente_teste['site_emissao']}")
        print(f"Mês/Ano: {parametros['mes_ano']}")
        
        # Executa RPA com dados do cliente
        resultado = digitalnet_rpa.executar_download(
            cliente_data=cliente_teste,
            parametros=parametros
        )
        
        if resultado['sucesso']:
            print("\n✅ SUCESSO: RPA DigitalNet executado com êxito")
            print(f"Arquivo baixado: {resultado.get('arquivo_baixado', 'N/A')}")
            print(f"URL S3: {resultado.get('url_s3', 'N/A')}")
            print(f"Tempo execução: {resultado.get('tempo_execucao', 'N/A')}s")
        else:
            print("\n❌ ERRO: Falha na execução do RPA DigitalNet")
            print(f"Mensagem: {resultado.get('mensagem_erro', 'Erro desconhecido')}")
            
        # Log detalhado para debug
        print(f"\n📋 LOGS DE EXECUÇÃO:")
        print(resultado.get('logs_execucao', 'Sem logs disponíveis'))
        
    except Exception as e:
        logger.error(f"Erro no teste RPA DigitalNet: {str(e)}")
        print(f"\n💥 EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()

def test_digitalnet_validation():
    """Testa validação de dados do cliente DigitalNet"""
    print("\n=== TESTE VALIDAÇÃO DIGITALNET ===")
    
    digitalnet_rpa = DigitalNetRPA()
    
    # Dados válidos para teste
    cliente_valido = {
        'cnpj': '23.456.789/0001-80',
        'login_portal': 'usuario_digitalnet',
        'senha_portal': 'senha_digitalnet_valida',
        'operadora_codigo': 'DIGITALNET'
    }
    
    try:
        validacao = digitalnet_rpa.validar_configuracao(cliente_valido)
        if validacao['valido']:
            print("✅ SUCESSO: Dados válidos aceitos")
        else:
            print("❌ ERRO: Dados válidos rejeitados")
            print(f"Erros: {validacao.get('erros', [])}")
    except Exception as e:
        print(f"Erro na validação: {str(e)}")

if __name__ == "__main__":
    # Executa testes individuais
    test_digitalnet_rpa_individual()
    test_digitalnet_validation()
    
    print("\n" + "="*50)
    print("TESTE INDIVIDUAL DIGITALNET RPA CONCLUÍDO")
    print("Verifique os logs para detalhes da execução")