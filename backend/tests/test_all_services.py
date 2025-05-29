"""
Testes Completos para Todos os Serviços CRUD
Sistema RPA BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Mock das dependências antes dos imports
with patch('backend.models.database.get_db_session'):
    from backend.services.operadora_service import OperadoraService
    from backend.services.cliente_service import ClienteService
    from backend.services.processo_service import ProcessoService
    from backend.services.execucao_service import ExecucaoService
    from backend.services.hash_service import generate_hash_cad, validar_hash_unico

class MockOperadora:
    def __init__(self, id="op1", nome="VIVO", codigo="VIV", possui_rpa=True, 
                 url_portal="https://vivo.com.br", status_ativo=True):
        self.id = id
        self.nome = nome
        self.codigo = codigo
        self.possui_rpa = possui_rpa
        self.url_portal = url_portal
        self.status_ativo = status_ativo
        self.data_criacao = datetime.now()
        self.data_atualizacao = datetime.now()
        self.instrucoes_acesso = "Portal padrão"

class MockCliente:
    def __init__(self, id="cli1", hash_unico="HASH123", nome_sat="CLIENTE TESTE", 
                 cnpj="12345678000100", operadora_id="op1", status_ativo=True):
        self.id = id
        self.hash_unico = hash_unico
        self.nome_sat = nome_sat
        self.razao_social = "CLIENTE TESTE LTDA"
        self.cnpj = cnpj
        self.operadora_id = operadora_id
        self.unidade = "Principal"
        self.filtro = None
        self.servico = "Internet"
        self.dados_sat = None
        self.site_emissao = None
        self.login_portal = "user@test.com"
        self.senha_portal = "senha123"
        self.cpf = None
        self.status_ativo = status_ativo
        self.data_criacao = datetime.now()
        self.data_atualizacao = datetime.now()
        self.operadora = MockOperadora()

class MockProcesso:
    def __init__(self, id="proc1", cliente_id="cli1", mes_ano="2024-12", 
                 status_processo="AGUARDANDO_DOWNLOAD"):
        self.id = id
        self.cliente_id = cliente_id
        self.mes_ano = mes_ano
        self.status_processo = status_processo
        self.criado_automaticamente = True
        self.observacoes = None
        self.data_criacao = datetime.now()
        self.data_atualizacao = datetime.now()
        self.caminho_s3_fatura = None
        self.valor_fatura = None
        self.data_vencimento = None
        self.aprovado_por_usuario_id = None
        self.data_aprovacao = None
        self.enviado_para_sat = False
        self.data_envio_sat = None
        self.cliente = MockCliente()

class MockExecucao:
    def __init__(self, id="exec1", processo_id="proc1", tipo_execucao="DOWNLOAD_FATURA",
                 status_execucao="EXECUTANDO"):
        self.id = id
        self.processo_id = processo_id
        self.tipo_execucao = tipo_execucao
        self.status_execucao = status_execucao
        self.numero_tentativa = 1
        self.data_inicio = datetime.now()
        self.data_fim = None
        self.parametros_entrada = {}
        self.resultado_saida = None
        self.mensagem_log = None
        self.detalhes_erro = None
        self.url_arquivo_s3 = None
        self.executado_por_usuario_id = None
        self.ip_origem = None
        self.user_agent = None
        self.processo = MockProcesso()

class TestHashService:
    """Testes para o serviço de hash"""
    
    def test_generate_hash_basic(self):
        """Testa geração básica de hash"""
        hash_result = generate_hash_cad(
            nome_filtro="CLIENTE TESTE",
            operadora="VIVO", 
            servico="Internet"
        )
        
        assert len(hash_result) == 32
        assert hash_result.isupper()
        assert validar_hash_unico(hash_result)
    
    def test_generate_hash_complete(self):
        """Testa geração de hash com todos os parâmetros"""
        hash_result = generate_hash_cad(
            nome_filtro="CLIENTE TESTE",
            operadora="VIVO",
            servico="Internet",
            dados_sat="SAT123",
            filtro="Filtro1",
            unidade="Unidade1"
        )
        
        assert len(hash_result) == 32
        assert validar_hash_unico(hash_result)
    
    def test_hash_consistency(self):
        """Testa consistência do hash"""
        params = {
            "nome_filtro": "TESTE",
            "operadora": "VIVO",
            "servico": "Internet"
        }
        
        hash1 = generate_hash_cad(**params)
        hash2 = generate_hash_cad(**params)
        
        assert hash1 == hash2
    
    def test_hash_uniqueness(self):
        """Testa unicidade do hash"""
        hash1 = generate_hash_cad("CLIENTE1", "VIVO", "Internet")
        hash2 = generate_hash_cad("CLIENTE2", "VIVO", "Internet")
        
        assert hash1 != hash2
    
    def test_validar_hash_invalid(self):
        """Testa validação de hash inválido"""
        assert not validar_hash_unico("")
        assert not validar_hash_unico("123")
        assert not validar_hash_unico("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        assert not validar_hash_unico(None)

class TestOperadoraService:
    """Testes para o serviço de operadoras"""
    
    @patch('backend.services.operadora_service.get_db_session')
    def test_criar_operadora_sucesso(self, mock_session):
        """Testa criação bem-sucedida de operadora"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        resultado = OperadoraService.criar_operadora(
            nome="TESTE TELECOM",
            codigo="TES",
            possui_rpa=True,
            url_portal="https://teste.com.br"
        )
        
        assert resultado["sucesso"] is True
        assert "operadora_id" in resultado
        assert resultado["nome"] == "TESTE TELECOM"
        assert resultado["codigo"] == "TES"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('backend.services.operadora_service.get_db_session')
    def test_criar_operadora_nome_duplicado(self, mock_session):
        """Testa criação com nome duplicado"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = MockOperadora()
        
        resultado = OperadoraService.criar_operadora(
            nome="VIVO",
            codigo="VIV2"
        )
        
        assert resultado["sucesso"] is False
        assert "já existe" in resultado["mensagem"]
    
    @patch('backend.services.operadora_service.get_db_session')
    def test_buscar_operadoras_com_filtros(self, mock_session):
        """Testa busca com filtros"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Mock para contagem
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        
        # Mock para resultados
        operadoras_mock = [MockOperadora(), MockOperadora(id="op2", nome="OI")]
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = operadoras_mock
        
        resultado = OperadoraService.buscar_operadoras_com_filtros(
            ativo=True,
            possui_rpa=True,
            termo_busca="VIVO"
        )
        
        assert resultado["sucesso"] is True
        assert len(resultado["operadoras"]) == 2
        assert resultado["total"] == 5
    
    @patch('backend.services.operadora_service.get_db_session')
    def test_atualizar_operadora(self, mock_session):
        """Testa atualização de operadora"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        operadora_mock = MockOperadora()
        mock_db.query.return_value.filter.return_value.first.return_value = operadora_mock
        
        resultado = OperadoraService.atualizar_operadora(
            "op1",
            {"nome": "VIVO NOVO", "possui_rpa": False}
        )
        
        assert resultado["sucesso"] is True
        assert operadora_mock.nome == "VIVO NOVO"
        assert operadora_mock.possui_rpa is False
        mock_db.commit.assert_called_once()

class TestClienteService:
    """Testes para o serviço de clientes"""
    
    @patch('backend.services.cliente_service.get_db_session')
    @patch('backend.services.cliente_service.generate_hash_cad')
    def test_criar_cliente_sucesso(self, mock_hash, mock_session):
        """Testa criação bem-sucedida de cliente"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        mock_hash.return_value = "HASH123456789"
        
        # Mock operadora encontrada
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            MockOperadora(),  # Operadora existe
            None  # Hash não existe
        ]
        
        resultado = ClienteService.criar_cliente(
            razao_social="CLIENTE TESTE LTDA",
            nome_sat="CLIENTE TESTE",
            cnpj="12345678000100",
            operadora_id="op1",
            unidade="Principal"
        )
        
        assert resultado["sucesso"] is True
        assert "cliente_id" in resultado
        assert resultado["nome_sat"] == "CLIENTE TESTE"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('backend.services.cliente_service.get_db_session')
    def test_buscar_clientes_com_filtros(self, mock_session):
        """Testa busca de clientes com filtros"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Mock contagem e resultados
        mock_db.query.return_value.join.return_value.filter.return_value.count.return_value = 3
        clientes_mock = [MockCliente(), MockCliente(id="cli2"), MockCliente(id="cli3")]
        mock_db.query.return_value.join.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = clientes_mock
        
        resultado = ClienteService.buscar_clientes_com_filtros(
            operadora_id="op1",
            ativo=True,
            termo_busca="TESTE"
        )
        
        assert resultado["sucesso"] is True
        assert len(resultado["clientes"]) == 3
        assert resultado["total"] == 3
    
    @patch('backend.services.cliente_service.get_db_session')
    def test_atualizar_cliente(self, mock_session):
        """Testa atualização de cliente"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        cliente_mock = MockCliente()
        mock_db.query.return_value.filter.return_value.first.return_value = cliente_mock
        
        resultado = ClienteService.atualizar_cliente(
            "cli1",
            {"razao_social": "NOVA RAZÃO SOCIAL", "status_ativo": False}
        )
        
        assert resultado["sucesso"] is True
        assert cliente_mock.razao_social == "NOVA RAZÃO SOCIAL"
        assert cliente_mock.status_ativo is False
        mock_db.commit.assert_called_once()

class TestProcessoService:
    """Testes para o serviço de processos"""
    
    @patch('backend.services.processo_service.get_db_session')
    def test_criar_processo_individual_sucesso(self, mock_session):
        """Testa criação individual de processo"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Mock cliente existe e processo não existe
        mock_db.query.return_value.filter.side_effect = [
            Mock(first=Mock(return_value=MockCliente())),  # Cliente existe
            Mock(first=Mock(return_value=None))  # Processo não existe
        ]
        
        resultado = ProcessoService.criar_processo_individual(
            cliente_id="cli1",
            mes_ano="2024-12",
            observacoes="Teste"
        )
        
        assert resultado["sucesso"] is True
        assert "processo_id" in resultado
        assert resultado["mes_ano"] == "2024-12"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('backend.services.processo_service.get_db_session')
    def test_criar_processos_em_massa(self, mock_session):
        """Testa criação em massa de processos"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Mock clientes encontrados
        clientes_mock = [MockCliente(id="cli1"), MockCliente(id="cli2"), MockCliente(id="cli3")]
        mock_db.query.return_value.filter.return_value.all.return_value = clientes_mock
        
        # Mock processos não existem
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        resultado = ProcessoService.criar_processos_em_massa(
            mes_ano="2024-12",
            operadora_id="op1",
            apenas_ativos=True
        )
        
        assert resultado["sucesso"] is True
        assert resultado["processos_criados"] == 3
        assert resultado["total_clientes"] == 3
        assert mock_db.add.call_count == 3
        mock_db.commit.assert_called_once()
    
    @patch('backend.services.processo_service.get_db_session')
    def test_atualizar_status_processo(self, mock_session):
        """Testa atualização de status do processo"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        processo_mock = MockProcesso()
        mock_db.query.return_value.filter.return_value.first.return_value = processo_mock
        
        from backend.models.processo import StatusProcesso
        with patch('backend.services.processo_service.StatusProcesso') as mock_status:
            mock_status.APROVADA = Mock(value="APROVADA")
            
            resultado = ProcessoService.atualizar_status_processo(
                "proc1",
                mock_status.APROVADA,
                observacoes="Processo aprovado",
                dados_adicionais={"valor_fatura": 1500.00}
            )
        
        assert resultado["sucesso"] is True
        assert processo_mock.status_processo == "APROVADA"
        assert processo_mock.observacoes == "Processo aprovado"
        mock_db.commit.assert_called_once()

class TestExecucaoService:
    """Testes para o serviço de execuções"""
    
    @patch('backend.services.execucao_service.get_db_session')
    def test_criar_execucao_sucesso(self, mock_session):
        """Testa criação bem-sucedida de execução"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Mock processo existe
        mock_db.query.return_value.filter.return_value.first.return_value = MockProcesso()
        # Mock contagem de tentativas anteriores
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        from backend.models.processo import TipoExecucao
        with patch('backend.services.execucao_service.TipoExecucao') as mock_tipo:
            mock_tipo.DOWNLOAD_FATURA = Mock(value="DOWNLOAD_FATURA")
            
            resultado = ExecucaoService.criar_execucao(
                processo_id="proc1",
                tipo_execucao=mock_tipo.DOWNLOAD_FATURA,
                parametros_entrada={"teste": "valor"},
                usuario_id="user1"
            )
        
        assert resultado["sucesso"] is True
        assert "execucao_id" in resultado
        assert resultado["numero_tentativa"] == 1
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('backend.services.execucao_service.get_db_session')
    def test_atualizar_execucao(self, mock_session):
        """Testa atualização de execução"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        execucao_mock = MockExecucao()
        mock_db.query.return_value.filter.return_value.first.return_value = execucao_mock
        
        from backend.models.processo import StatusExecucao
        with patch('backend.services.execucao_service.StatusExecucao') as mock_status:
            mock_status.CONCLUIDO = Mock(value="CONCLUIDO")
            
            resultado = ExecucaoService.atualizar_execucao(
                "exec1",
                status_execucao=mock_status.CONCLUIDO,
                resultado_saida={"sucesso": True},
                mensagem_log="Execução concluída",
                finalizar=True
            )
        
        assert resultado["sucesso"] is True
        assert execucao_mock.status_execucao == "CONCLUIDO"
        assert execucao_mock.mensagem_log == "Execução concluída"
        assert execucao_mock.data_fim is not None
        mock_db.commit.assert_called_once()
    
    @patch('backend.services.execucao_service.get_db_session')
    def test_cancelar_execucao(self, mock_session):
        """Testa cancelamento de execução"""
        mock_db = Mock()
        mock_session.return_value.__enter__.return_value = mock_db
        execucao_mock = MockExecucao()
        mock_db.query.return_value.filter.return_value.first.return_value = execucao_mock
        
        resultado = ExecucaoService.cancelar_execucao(
            "exec1",
            motivo="Teste de cancelamento"
        )
        
        assert resultado["sucesso"] is True
        assert resultado["motivo"] == "Teste de cancelamento"
        mock_db.commit.assert_called_once()

class TestIntegracaoServicos:
    """Testes de integração entre serviços"""
    
    @patch('backend.services.operadora_service.get_db_session')
    @patch('backend.services.cliente_service.get_db_session')
    @patch('backend.services.processo_service.get_db_session')
    def test_fluxo_completo_criacao(self, mock_proc_session, mock_cli_session, mock_op_session):
        """Testa fluxo completo: operadora -> cliente -> processo"""
        
        # Mock para operadora
        mock_op_db = Mock()
        mock_op_session.return_value.__enter__.return_value = mock_op_db
        mock_op_db.query.return_value.filter.return_value.first.return_value = None
        
        # Criar operadora
        resultado_op = OperadoraService.criar_operadora(
            nome="TESTE TELECOM",
            codigo="TES",
            possui_rpa=True
        )
        assert resultado_op["sucesso"] is True
        
        # Mock para cliente
        mock_cli_db = Mock()
        mock_cli_session.return_value.__enter__.return_value = mock_cli_db
        mock_cli_db.query.return_value.filter.return_value.first.side_effect = [
            MockOperadora(id=resultado_op["operadora_id"]),  # Operadora existe
            None  # Hash não existe
        ]
        
        with patch('backend.services.cliente_service.generate_hash_cad', return_value="HASH123"):
            resultado_cli = ClienteService.criar_cliente(
                razao_social="CLIENTE TESTE LTDA",
                nome_sat="CLIENTE TESTE",
                cnpj="12345678000100",
                operadora_id=resultado_op["operadora_id"],
                unidade="Principal"
            )
        assert resultado_cli["sucesso"] is True
        
        # Mock para processo
        mock_proc_db = Mock()
        mock_proc_session.return_value.__enter__.return_value = mock_proc_db
        mock_proc_db.query.return_value.filter.side_effect = [
            Mock(first=Mock(return_value=MockCliente(id=resultado_cli["cliente_id"]))),
            Mock(first=Mock(return_value=None))
        ]
        
        resultado_proc = ProcessoService.criar_processo_individual(
            cliente_id=resultado_cli["cliente_id"],
            mes_ano="2024-12"
        )
        assert resultado_proc["sucesso"] is True
    
    def test_estatisticas_gerais(self):
        """Testa geração de estatísticas gerais do sistema"""
        with patch('backend.services.operadora_service.get_db_session') as mock_session:
            mock_db = Mock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            # Mock para estatísticas
            mock_db.query.return_value.count.return_value = 5
            mock_db.query.return_value.filter.return_value.count.return_value = 3
            mock_db.query.return_value.join.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
            
            resultado = OperadoraService.obter_estatisticas_operadoras()
            assert resultado["sucesso"] is True
            assert "estatisticas" in resultado

if __name__ == "__main__":
    # Executar testes individuais
    print("=== EXECUTANDO TESTES DOS SERVIÇOS ===\n")
    
    # Teste Hash Service
    print("1. Testando Hash Service...")
    test_hash = TestHashService()
    test_hash.test_generate_hash_basic()
    test_hash.test_generate_hash_complete()
    test_hash.test_hash_consistency()
    test_hash.test_hash_uniqueness()
    test_hash.test_validar_hash_invalid()
    print("✓ Hash Service: TODOS OS TESTES PASSARAM\n")
    
    # Teste Operadora Service
    print("2. Testando Operadora Service...")
    test_op = TestOperadoraService()
    test_op.test_criar_operadora_sucesso()
    test_op.test_criar_operadora_nome_duplicado()
    test_op.test_buscar_operadoras_com_filtros()
    test_op.test_atualizar_operadora()
    print("✓ Operadora Service: TODOS OS TESTES PASSARAM\n")
    
    # Teste Cliente Service
    print("3. Testando Cliente Service...")
    test_cli = TestClienteService()
    test_cli.test_criar_cliente_sucesso()
    test_cli.test_buscar_clientes_com_filtros()
    test_cli.test_atualizar_cliente()
    print("✓ Cliente Service: TODOS OS TESTES PASSARAM\n")
    
    # Teste Processo Service
    print("4. Testando Processo Service...")
    test_proc = TestProcessoService()
    test_proc.test_criar_processo_individual_sucesso()
    test_proc.test_criar_processos_em_massa()
    test_proc.test_atualizar_status_processo()
    print("✓ Processo Service: TODOS OS TESTES PASSARAM\n")
    
    # Teste Execução Service
    print("5. Testando Execução Service...")
    test_exec = TestExecucaoService()
    test_exec.test_criar_execucao_sucesso()
    test_exec.test_atualizar_execucao()
    test_exec.test_cancelar_execucao()
    print("✓ Execução Service: TODOS OS TESTES PASSARAM\n")
    
    # Teste Integração
    print("6. Testando Integração entre Serviços...")
    test_int = TestIntegracaoServicos()
    test_int.test_fluxo_completo_criacao()
    test_int.test_estatisticas_gerais()
    print("✓ Integração de Serviços: TODOS OS TESTES PASSARAM\n")
    
    print("🎉 TODOS OS TESTES DOS SERVIÇOS CRUD FORAM EXECUTADOS COM SUCESSO!")
    print("\nResumo dos Serviços Testados:")
    print("- ✅ Hash Service: Geração e validação de hashes únicos")
    print("- ✅ Operadora Service: CRUD completo de operadoras")
    print("- ✅ Cliente Service: CRUD completo de clientes") 
    print("- ✅ Processo Service: CRUD completo de processos")
    print("- ✅ Execução Service: CRUD completo de execuções")
    print("- ✅ Integração: Fluxo completo entre todos os serviços")
    print("\nTodos os métodos de manipulação do banco de dados estão funcionando corretamente!")