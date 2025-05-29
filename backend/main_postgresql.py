"""
Backend Principal com PostgreSQL - Sistema RPA BGTELECOM
Integração completa com dados reais da BGTELECOM
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import uvicorn
import os

# Importar conexão PostgreSQL
from backend.database_postgresql import (
    operadora_service, cliente_service, processo_service, 
    execucao_service, dashboard_service
)

app = FastAPI(
    title="Sistema RPA BGTELECOM - PostgreSQL",
    description="Sistema de Orquestração RPA com dados reais da BGTELECOM",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class AprovacaoRequest(BaseModel):
    aprovadoPor: int
    observacoes: Optional[str] = None

class RejeicaoRequest(BaseModel):
    motivoRejeicao: str

# ===== DASHBOARD ENDPOINTS =====
@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Métricas do dashboard em tempo real"""
    try:
        return dashboard_service.obter_metricas_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
async def get_dashboard():
    """Dados principais do dashboard"""
    try:
        return dashboard_service.obter_metricas_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== OPERADORAS ENDPOINTS =====
@app.get("/api/operadoras")
async def get_operadoras(
    ativo: Optional[bool] = Query(None),
    possui_rpa: Optional[bool] = Query(None)
):
    """Listar operadoras"""
    try:
        return operadora_service.listar_operadoras(ativo, possui_rpa)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rpa/status")
async def get_rpa_status():
    """Status dos RPAs"""
    try:
        return operadora_service.obter_status_rpas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CLIENTES ENDPOINTS =====
@app.get("/api/clientes")
async def get_clientes(
    operadora_id: Optional[int] = Query(None),
    ativo: Optional[bool] = Query(None),
    termo_busca: Optional[str] = Query(None)
):
    """Listar clientes"""
    try:
        return cliente_service.listar_clientes(operadora_id, ativo, termo_busca)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== PROCESSOS/FATURAS ENDPOINTS =====
@app.get("/api/faturas")
async def get_faturas(
    statusAprovacao: Optional[str] = Query(None),
    operadora_id: Optional[int] = Query(None),
    mes_ano: Optional[str] = Query(None)
):
    """Listar faturas/processos"""
    try:
        if statusAprovacao == "pendente":
            return processo_service.listar_processos(mes_ano, "PENDENTE_APROVACAO", operadora_id)
        elif statusAprovacao == "aprovada":
            return processo_service.listar_processos(mes_ano, "APROVADA", operadora_id)
        else:
            return processo_service.listar_processos(mes_ano, None, operadora_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/faturas/{faturaId}/aprovar")
async def aprovar_fatura(faturaId: int, request: AprovacaoRequest):
    """Aprovar fatura"""
    try:
        return processo_service.aprovar_processo(
            faturaId, str(request.aprovadoPor), request.observacoes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/faturas/{faturaId}/rejeitar")
async def rejeitar_fatura(faturaId: int, request: RejeicaoRequest):
    """Rejeitar fatura"""
    try:
        return processo_service.rejeitar_processo(faturaId, request.motivoRejeicao)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== EXECUÇÕES ENDPOINTS =====
@app.get("/api/execucoes")
async def get_execucoes(
    status: Optional[str] = Query(None),
    operadora: Optional[str] = Query(None)
):
    """Listar execuções"""
    try:
        return execucao_service.listar_execucoes(status, operadora)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/execucoes/ativas")
async def get_execucoes_ativas():
    """Execuções ativas"""
    try:
        return execucao_service.obter_execucoes_ativas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execucoes/{execucaoId}/cancel")
async def cancelar_execucao(execucaoId: int):
    """Cancelar execução"""
    try:
        return execucao_service.cancelar_execucao(execucaoId, "Cancelado pelo usuário")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== NOTIFICAÇÕES ENDPOINTS =====
@app.get("/api/notificacoes")
async def get_notificacoes(
    tipo: Optional[str] = Query(None),
    lida: Optional[bool] = Query(None)
):
    """Listar notificações"""
    try:
        metricas = dashboard_service.obter_metricas_dashboard()
        alertas = metricas.get("alertas", [])
        
        notificacoes = []
        for alerta in alertas:
            notificacoes.append({
                "id": f"alert_{hash(alerta['titulo'])}",
                "tipo": alerta["tipo"],
                "titulo": alerta["titulo"],
                "mensagem": alerta["descricao"],
                "data": datetime.now().isoformat(),
                "lida": False
            })
        
        # Filtros
        if tipo:
            notificacoes = [n for n in notificacoes if n["tipo"] == tipo]
        if lida is not None:
            notificacoes = [n for n in notificacoes if n["lida"] == lida]
        
        return notificacoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== AUTENTICAÇÃO ENDPOINTS =====
@app.post("/api/auth/login")
async def login(request: dict):
    """Login de usuário"""
    # Simulação de autenticação para teste
    email = request.get("email")
    senha = request.get("senha")
    
    if email == "admin@bgtelecom.com.br" and senha == "admin123":
        return {
            "sucesso": True,
            "usuario": {
                "id": 1,
                "nome": "Administrador BGTELECOM",
                "email": email,
                "tipo_usuario": "ADMINISTRADOR"
            },
            "token": "jwt_token_simulado"
        }
    else:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    """Health check do sistema"""
    try:
        metricas = dashboard_service.obter_metricas_dashboard()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "PostgreSQL",
            "dados": "BGTELECOM Autênticos",
            "metricas": metricas["metricas"]
        }
    except Exception as e:
        return {"status": "error", "erro": str(e)}

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "sistema": "RPA BGTELECOM",
        "versao": "1.0.0",
        "status": "ativo",
        "database": "PostgreSQL",
        "dados": "Autênticos BGTELECOM"
    }

# ===== TESTE DE DADOS =====
@app.get("/test/dados")
async def test_dados():
    """Endpoint para testar dados autênticos"""
    try:
        # Testar cada serviço
        operadoras = operadora_service.listar_operadoras()
        clientes = cliente_service.listar_clientes()
        processos = processo_service.listar_processos()
        execucoes = execucao_service.listar_execucoes()
        dashboard = dashboard_service.obter_metricas_dashboard()
        
        return {
            "teste_completo": "SUCESSO",
            "operadoras": operadoras["total"],
            "clientes": clientes["total"],
            "processos": processos["total"],
            "execucoes": execucoes["total"],
            "dashboard_metricas": dashboard["metricas"],
            "clientes_exemplo": clientes["clientes"][:3] if clientes["clientes"] else [],
            "processos_pendentes": [
                p for p in processos["processos"] 
                if p["status_processo"] == "PENDENTE_APROVACAO"
            ][:5] if processos["processos"] else []
        }
    except Exception as e:
        return {"teste_completo": "ERRO", "erro": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print(f"""
🚀 SISTEMA RPA BGTELECOM - POSTGRESQL
====================================
🌐 Servidor: http://localhost:{port}
📋 Documentação: http://localhost:{port}/docs
🔧 Health Check: http://localhost:{port}/health
🧪 Teste Dados: http://localhost:{port}/test/dados
📊 Dashboard: http://localhost:{port}/api/dashboard/metrics

📈 DADOS AUTÊNTICOS BGTELECOM:
   ✓ 6 Operadoras (EMBRATEL, DIGITALNET, AZUTON, VIVO, OI, SAT)
   ✓ 12 Clientes reais (RICAL, ALVORADA, CENZE, FINANCIAL, etc.)
   ✓ 15 Processos com valores reais
   ✓ 8 Execuções RPA ativas/históricas
   ✓ PostgreSQL como banco principal
====================================
    """)
    
    uvicorn.run(
        "backend.main_postgresql:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )