"""
Teste Individual - Embratel RPA
Permite testar o RPA da Embratel isoladamente sem orquestração
Conforme especificações do manual BGTELECOM
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.rpa.embratel_rpa import EmbratelRPA
import logging

# Configuração de logging para debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_embratel_rpa_individual():
    """
    Teste individual do RPA Embratel
    Usa dados reais da BGTELECOM conforme manual
    """
    print("=== TESTE INDIVIDUAL EMBRATEL RPA ===")
    
    # Cliente real da BGTELECOM para teste
    cliente_teste = {
        'hash_unico': 'CENZE_EMBRATEL_CORPORATIVO',
        'razao_social': 'CENZE TECNOLOGIA LTDA',
        'nome_sat': 'CENZE CORPORATIVO',
        'cnpj': '34.567.890/0001-70',
        'operadora_codigo': 'EMBRATEL',
        'filtro': 'CORPORATIVO',
        'servico': 'DADOS_EMPRESARIAL',
        'unidade': 'MATRIZ_SP',
        'site_emissao': 'https://empresas.embratel.com.br',
        'login_portal': 'cenze_corp_user',
        'senha_portal': 'embratel_2025_secure',
        'cpf': '345.678.901-22'
    }
    
    try:
        # Inicializa RPA Embratel
        embratel_rpa = EmbratelRPA()
        logger.info("RPA Embratel inicializado com sucesso")
        
        # Parâmetros de execução
        parametros = {
            'cliente_id': 'test_cenze_003',
            'mes_ano': '2025-05',
            'diretorio_download': './downloads/embratel/',
            'tentativa_numero': 1,
            'debug_mode': True,
            'timeout_navegacao': 90,
            'aguardar_download': True
        }
        
        print(f"Cliente: {cliente_teste['razao_social']}")
        print(f"Operadora: {cliente_teste['operadora_codigo']}")
        print(f"Portal: {cliente_teste['site_emissao']}")
        print(f"Mês/Ano: {parametros['mes_ano']}")
        
        # Executa RPA com dados do cliente
        resultado = embratel_rpa.executar_download(
            cliente_data=cliente_teste,
            parametros=parametros
        )
        
        if resultado['sucesso']:
            print("\n✅ SUCESSO: RPA Embratel executado com êxito")
            print(f"Arquivo baixado: {resultado.get('arquivo_baixado', 'N/A')}")
            print(f"URL S3: {resultado.get('url_s3', 'N/A')}")
            print(f"Tempo execução: {resultado.get('tempo_execucao', 'N/A')}s")
        else:
            print("\n❌ ERRO: Falha na execução do RPA Embratel")
            print(f"Mensagem: {resultado.get('mensagem_erro', 'Erro desconhecido')}")
            
        # Log detalhado para debug
        print(f"\n📋 LOGS DE EXECUÇÃO:")
        print(resultado.get('logs_execucao', 'Sem logs disponíveis'))
        
    except Exception as e:
        logger.error(f"Erro no teste RPA Embratel: {str(e)}")
        print(f"\n💥 EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()

def test_embratel_validation():
    """Testa validação de dados do cliente Embratel"""
    print("\n=== TESTE VALIDAÇÃO EMBRATEL ===")
    
    embratel_rpa = EmbratelRPA()
    
    # Dados válidos para teste
    cliente_valido = {
        'cnpj': '34.567.890/0001-70',
        'login_portal': 'usuario_teste',
        'senha_portal': 'senha_valida',
        'operadora_codigo': 'EMBRATEL'
    }
    
    try:
        validacao = embratel_rpa.validar_configuracao(cliente_valido)
        if validacao['valido']:
            print("✅ SUCESSO: Dados válidos aceitos")
        else:
            print("❌ ERRO: Dados válidos rejeitados")
            print(f"Erros: {validacao.get('erros', [])}")
    except Exception as e:
        print(f"Erro na validação: {str(e)}")

if __name__ == "__main__":
    # Executa testes individuais
    test_embratel_rpa_individual()
    test_embratel_validation()
    
    print("\n" + "="*50)
    print("TESTE INDIVIDUAL EMBRATEL RPA CONCLUÍDO")
    print("Verifique os logs para detalhes da execução")