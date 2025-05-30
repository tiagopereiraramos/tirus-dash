"""
Rotas da API para o Frontend
Sistema RPA BGTELECOM
Todas as rotas necessárias para as páginas do frontend
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api")

# ===== MODELOS PYDANTIC =====
class AprovacaoRequest(BaseModel):
    observacoes: Optional[str] = None

class RejeicaoRequest(BaseModel):
    motivo_rejeicao: str
    observacoes: Optional[str] = None

class AprovacaoLoteRequest(BaseModel):
    processo_ids: List[str]
    observacoes: Optional[str] = None

class ClienteRequest(BaseModel):
    razao_social: str
    nome_sat: str
    cnpj: str
    operadora_id: str
    unidade: str
    filtro: Optional[str] = None
    servico: Optional[str] = None
    dados_sat: Optional[str] = None
    site_emissao: Optional[str] = None
    login_portal: Optional[str] = None
    senha_portal: Optional[str] = None
    cpf: Optional[str] = None

class ProcessoRequest(BaseModel):
    cliente_id: str
    mes_ano: str
    observacoes: Optional[str] = None

class ProcessoMassaRequest(BaseModel):
    mes_ano: str
    operadora_id: Optional[str] = None
    apenas_ativos: bool = True

class UsuarioRequest(BaseModel):
    nome: str
    email: str
    senha: str
    tipo_usuario: str = "OPERADOR"
    telefone: Optional[str] = None
    departamento: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    senha: str

# ===== DASHBOARD ROUTES =====
@router.get("/dashboard")
async def get_dashboard():
    """Dados principais do dashboard - usado pela página Dashboard"""
    return {
        "operadoras": 6,
        "clientes": 12,
        "processos": 0,
        "status": "online"
    }

@router.get("/dashboard/metrics")
async def get_dashboard_metrics():
    """Métricas em tempo real - usado pela página Dashboard"""
    return {
        "operadoras": 6,
        "clientes": 12,
        "processos": 0,
        "execucoes_ativas": 0
    }

@router.get("/dashboard/complete")
async def get_dashboard_complete():
    """Dados completos do dashboard - usado pela página Dashboard"""
    return {
        "operadoras": 6,
        "clientes": 12,
        "processos": 0,
        "status": "online",
        "sistema": "RPA BGTELECOM"
    }

# ===== APROVAÇÕES ROUTES =====
@router.get("/faturas")
async def get_faturas(
    statusAprovacao: Optional[str] = Query(None),
    operadora_id: Optional[str] = Query(None),
    valor_minimo: Optional[float] = Query(None),
    valor_maximo: Optional[float] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """Listar faturas - usado pela página Aprovações"""
    try:
        if statusAprovacao == "pendente":
            from backend.services.aprovacao_service import AprovacaoService
            return AprovacaoService.obter_faturas_pendentes_aprovacao(
                operadora_id, valor_minimo, valor_maximo, skip, limit
            )
        elif statusAprovacao == "aprovada":
            from backend.services.aprovacao_service import AprovacaoService
            return AprovacaoService.obter_historico_aprovacoes(
                None, None, None, skip, limit
            )
        else:
            from backend.services.processo_service import ProcessoService
            return ProcessoService.buscar_processos_com_filtros(
                None, None, operadora_id, None, skip, limit
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/faturas/{fatura_id}/aprovar")
async def aprovar_fatura(fatura_id: str, request: AprovacaoRequest):
    """Aprovar fatura - usado pela página Aprovações"""
    try:
        from backend.services.aprovacao_service import AprovacaoService
        usuario_id = "user1"  # TODO: Pegar do sistema de autenticação
        return AprovacaoService.aprovar_fatura(
            fatura_id, usuario_id, request.observacoes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/faturas/{fatura_id}/rejeitar")
async def rejeitar_fatura(fatura_id: str, request: RejeicaoRequest):
    """Rejeitar fatura - usado pela página Aprovações"""
    try:
        from backend.services.aprovacao_service import AprovacaoService
        usuario_id = "user1"  # TODO: Pegar do sistema de autenticação
        return AprovacaoService.rejeitar_fatura(
            fatura_id, usuario_id, request.motivo_rejeicao
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== EXECUÇÕES ROUTES =====
@router.get("/execucoes")
async def get_execucoes(
    processo_id: Optional[str] = Query(None),
    tipo_execucao: Optional[str] = Query(None),
    status_execucao: Optional[str] = Query(None),
    operadora_id: Optional[str] = Query(None),
    apenas_ativas: bool = Query(False),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """Listar execuções - usado pela página Execuções"""
    try:
        from backend.services.execucao_service import ExecucaoService
        return ExecucaoService.buscar_execucoes_com_filtros(
            processo_id, None, None, operadora_id,
            None, None, apenas_ativas, skip, limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/execucoes/ativas")
async def get_execucoes_ativas():
    """Execuções ativas - usado pela página Execuções e Dashboard"""
    try:
        from backend.services.execucao_service import ExecucaoService
        return ExecucaoService.obter_execucoes_ativas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execucoes/{execucao_id}/cancelar")
async def cancelar_execucao(execucao_id: str, motivo: str = "Cancelado pelo usuário"):
    """Cancelar execução - usado pela página Execuções"""
    try:
        from backend.services.execucao_service import ExecucaoService
        return ExecucaoService.cancelar_execucao(execucao_id, motivo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CLIENTES ROUTES =====
@router.get("/clientes")
async def get_clientes(
    operadora_id: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    termo_busca: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """Listar clientes - usado pela página Clientes"""
    try:
        from backend.services.cliente_service import ClienteService
        return ClienteService.buscar_clientes_com_filtros(
            operadora_id, ativo, termo_busca, skip, limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clientes")
async def criar_cliente(request: ClienteRequest):
    """Criar cliente - usado pela página Clientes"""
    try:
        from backend.services.cliente_service import ClienteService
        return ClienteService.criar_cliente(
            razao_social=request.razao_social,
            nome_sat=request.nome_sat,
            cnpj=request.cnpj,
            operadora_id=request.operadora_id,
            unidade=request.unidade,
            filtro=request.filtro,
            servico=request.servico,
            dados_sat=request.dados_sat,
            site_emissao=request.site_emissao,
            login_portal=request.login_portal,
            senha_portal=request.senha_portal,
            cpf=request.cpf
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== OPERADORAS ROUTES =====
@router.get("/operadoras")
async def get_operadoras(
    ativo: Optional[bool] = Query(None),
    possui_rpa: Optional[bool] = Query(None),
    termo_busca: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100)
):
    """Listar operadoras - usado pela página Operadoras"""
    try:
        from backend.services.operadora_service import OperadoraService
        return OperadoraService.buscar_operadoras_com_filtros(
            ativo, possui_rpa, termo_busca, skip, limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/operadoras/inicializar-padrao")
async def inicializar_operadoras_padrao():
    """Inicializar operadoras padrão - usado pela página Operadoras"""
    try:
        from backend.services.operadora_service import OperadoraService
        return OperadoraService.inicializar_operadoras_padrao()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== PROCESSOS ROUTES =====
@router.post("/processos")
async def criar_processo(request: ProcessoRequest):
    """Criar processo individual - usado pela página Cadastro"""
    try:
        from backend.services.processo_service import ProcessoService
        return ProcessoService.criar_processo_individual(
            cliente_id=request.cliente_id,
            mes_ano=request.mes_ano,
            observacoes=request.observacoes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/processos/massa")
async def criar_processos_massa(request: ProcessoMassaRequest):
    """Criar processos em massa - usado pela página Cadastro"""
    try:
        from backend.services.processo_service import ProcessoService
        return ProcessoService.criar_processos_em_massa(
            mes_ano=request.mes_ano,
            operadora_id=request.operadora_id,
            apenas_ativos=request.apenas_ativos
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== USUÁRIOS ROUTES =====
@router.post("/auth/login")
async def login(request: LoginRequest):
    """Login de usuário - usado pela página Login"""
    try:
        from backend.services.usuario_service import UsuarioService
        return UsuarioService.autenticar_usuario(
            email=request.email,
            senha=request.senha
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

# ===== NOTIFICAÇÕES ROUTES =====
@router.get("/notificacoes")
async def get_notificacoes(
    tipo: Optional[str] = Query(None),
    lida: Optional[bool] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50)
):
    """Listar notificações - usado pela página Notificações"""
    try:
        from backend.services.dashboard_service import DashboardService
        alertas = DashboardService.obter_alertas_sistema()
        
        notificacoes = []
        for alerta in alertas.get("alertas", []):
            notificacoes.append({
                "id": f"alert_{hash(alerta['titulo'])}",
                "tipo": alerta["tipo"],
                "titulo": alerta["titulo"],
                "mensagem": alerta["descricao"],
                "data": alerta.get("data", datetime.now().isoformat()),
                "lida": False,
                "severidade": alerta.get("severidade", "BAIXA")
            })
        
        return {
            "sucesso": True,
            "notificacoes": notificacoes[skip:skip+limit],
            "total": len(notificacoes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== RPA STATUS ROUTES =====
@router.get("/rpa/status")
async def get_rpa_status():
    """Status dos RPAs - usado pelas páginas Dashboard e Execuções"""
    try:
        from backend.services.execucao_service import ExecucaoService
        from backend.services.operadora_service import OperadoraService
        
        execucoes_ativas = ExecucaoService.obter_execucoes_ativas()
        operadoras = OperadoraService.buscar_operadoras_com_filtros(possui_rpa=True)
        
        status_por_operadora = {}
        
        for operadora in operadoras.get("operadoras", []):
            codigo = operadora["codigo"]
            execucoes_operadora = [
                e for e in execucoes_ativas.get("execucoes_ativas", [])
                if e.get("operadora") == operadora["nome"]
            ]
            
            status_por_operadora[codigo] = {
                "operadora": operadora["nome"],
                "codigo": codigo,
                "possui_rpa": operadora["possui_rpa"],
                "execucoes_ativas": len(execucoes_operadora),
                "disponivel": operadora["possui_rpa"] and len(execucoes_operadora) == 0,
                "ultima_execucao": execucoes_operadora[0] if execucoes_operadora else None
            }
        
        return {
            "status": "success",
            "operadoras": status_por_operadora,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))