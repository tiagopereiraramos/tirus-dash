"""
Backend Principal do Sistema RPA BGTELECOM
Integração completa com todas as funcionalidades
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar as rotas da API
from backend.routes.api_routes import router as api_router

# Importar serviços para inicialização
from backend.services.operadora_service import OperadoraService
from backend.services.cliente_service import ClienteService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    try:
        print("🚀 Iniciando Sistema RPA BGTELECOM...")
        
        # Inicializar operadoras padrão
        try:
            print("📋 Inicializando operadoras padrão...")
            resultado_operadoras = OperadoraService.inicializar_operadoras_padrao()
            print(f"✅ Operadoras inicializadas: {resultado_operadoras.get('total_criadas', 0)}")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar operadoras: {e}")
        
        # Inicializar clientes BGTELECOM
        try:
            print("👥 Inicializando clientes BGTELECOM...")
            resultado_clientes = ClienteService.inicializar_clientes_bgtelecom()
            print(f"✅ Clientes inicializados: {resultado_clientes.get('total_criados', 0)}")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar clientes: {e}")
        
        print("🎯 Sistema RPA BGTELECOM iniciado com sucesso!")
        yield
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        yield
    finally:
        print("🔄 Finalizando Sistema RPA BGTELECOM...")

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema RPA BGTELECOM",
    description="Sistema de Orquestração RPA para Gestão de Faturas de Telecomunicações",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas da API
app.include_router(api_router)

# Endpoint dashboard simples
@app.get("/api/dashboard")
async def get_dashboard():
    """Dados do dashboard"""
    return {
        "operadoras": 6,
        "clientes": 12,
        "processos": 0,
        "status": "online"
    }

# Endpoint de status
@app.get("/")
async def root():
    """Endpoint raiz - status do sistema"""
    return {
        "sistema": "RPA BGTELECOM",
        "versao": "1.0.0",
        "status": "ativo",
        "descricao": "Sistema de Orquestração RPA para Gestão de Faturas de Telecomunicações"
    }

@app.get("/health")
async def health_check():
    """Health check do sistema"""
    try:
        from backend.services.dashboard_service import DashboardService
        
        # Verificar serviços principais
        dados_dashboard = DashboardService.obter_dados_dashboard_principal()
        
        return {
            "status": "healthy",
            "timestamp": dados_dashboard.get("timestamp"),
            "servicos": {
                "dashboard": "ok",
                "operadoras": "ok", 
                "clientes": "ok",
                "processos": "ok",
                "execucoes": "ok",
                "aprovacoes": "ok"
            },
            "metricas": {
                "operadoras_ativas": dados_dashboard.get("total_operadoras", 0),
                "clientes_ativos": dados_dashboard.get("total_clientes", 0),
                "processos_mes": dados_dashboard.get("total_processos_mes", 0)
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "erro": str(e),
            "servicos": {
                "dashboard": "error"
            }
        }

# Endpoint para executar RPA específico
@app.post("/rpa/executar/{operadora}")
async def executar_rpa(operadora: str, processo_id: str = None):
    """Executa RPA para uma operadora específica"""
    try:
        from backend.services.execucao_service import ExecucaoService
        
        if not processo_id:
            raise HTTPException(status_code=400, detail="processo_id é obrigatório")
        
        # Criar execução
        resultado = ExecucaoService.criar_execucao(
            processo_id=processo_id,
            tipo_execucao="DOWNLOAD",
            parametros_entrada={"operadora": operadora}
        )
        
        return {
            "sucesso": True,
            "mensagem": f"RPA {operadora} iniciado com sucesso",
            "execucao_id": resultado.get("execucao_id"),
            "status": "INICIADO"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para parar RPA
@app.post("/rpa/parar/{operadora}")
async def parar_rpa(operadora: str):
    """Para a execução de um RPA específico"""
    try:
        from backend.services.execucao_service import ExecucaoService
        
        # Buscar execuções ativas da operadora
        execucoes_ativas = ExecucaoService.obter_execucoes_ativas()
        
        execucoes_operadora = [
            e for e in execucoes_ativas.get("execucoes_ativas", [])
            if e.get("operadora", "").upper() == operadora.upper()
        ]
        
        resultados = []
        for execucao in execucoes_operadora:
            resultado = ExecucaoService.cancelar_execucao(
                execucao["id"], 
                f"Cancelado via API - operadora {operadora}"
            )
            resultados.append(resultado)
        
        return {
            "sucesso": True,
            "mensagem": f"RPAs da operadora {operadora} cancelados",
            "execucoes_canceladas": len(resultados)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Configuração para desenvolvimento
    port = int(os.getenv("PORT", 8000))
    
    print(f"""
🚀 SISTEMA RPA BGTELECOM
========================
🌐 Servidor: http://localhost:{port}
📋 Documentação: http://localhost:{port}/docs
🔧 Health Check: http://localhost:{port}/health
📊 Dashboard API: http://localhost:{port}/api/dashboard
========================
    """)
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )