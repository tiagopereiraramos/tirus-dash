"""
Rotas principais da API
Sistema de Orquestração RPA - BGTELECOM
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from config.database import obter_db
from models.operadora import Operadora
from models.cliente import Cliente
from schemas.operadora_schemas import OperadoraResponse
from schemas.cliente_schemas import ClienteResponse
from services.rpa_service import RPAService

router_principal = APIRouter()

# Instância do serviço RPA
rpa_service = RPAService()

@router_principal.get("/")
async def status_api():
    """Status da API"""
    return {
        "sistema": "Orquestrador RPA BGTELECOM",
        "versao": "1.0.0",
        "status": "ativo",
        "desenvolvido_por": "Tiago Pereira Ramos"
    }

@router_principal.get("/health")
async def verificar_saude_sistema(db: Session = Depends(obter_db)):
    """Verifica a saúde geral do sistema"""
    try:
        # Verificar conexão com banco
        total_operadoras = db.query(Operadora).count()
        total_clientes = db.query(Cliente).count()
        
        # Verificar status dos RPAs
        status_rpas = rpa_service.obter_status_todos_rpas()
        
        return {
            "database": "conectado",
            "total_operadoras": total_operadoras,
            "total_clientes": total_clientes,
            "rpas": status_rpas,
            "status": "saudavel"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na verificação de saúde: {str(e)}"
        )

@router_principal.get("/operadoras", response_model=List[OperadoraResponse])
async def listar_operadoras(db: Session = Depends(obter_db)):
    """Lista todas as operadoras"""
    try:
        operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).all()
        return operadoras
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar operadoras: {str(e)}"
        )

@router_principal.get("/clientes", response_model=List[ClienteResponse])
async def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    operadora_id: Optional[str] = None,
    db: Session = Depends(obter_db)
):
    """Lista clientes com filtros opcionais"""
    try:
        query = db.query(Cliente).filter(Cliente.status_ativo == True)
        
        if operadora_id:
            query = query.filter(Cliente.operadora_id == operadora_id)
        
        clientes = query.offset(skip).limit(limit).all()
        return clientes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar clientes: {str(e)}"
        )

@router_principal.post("/rpa/executar/{operadora}")
async def executar_rpa(
    operadora: str,
    cliente_id: Optional[str] = None,
    mes_ano: Optional[str] = None,
    hash_execucao: Optional[str] = None
):
    """Executa RPA para uma operadora específica"""
    try:
        operadora_upper = operadora.upper()
        
        if operadora_upper not in ["VIVO", "OI", "EMBRATEL", "SAT", "AZUTON", "DIGITALNET"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Operadora não suportada: {operadora}"
            )
        
        resultado = rpa_service.executar_rpa(
            operadora=operadora_upper,
            cliente_id=cliente_id,
            mes_ano=mes_ano,
            hash_execucao=hash_execucao
        )
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar RPA: {str(e)}"
        )

@router_principal.get("/rpa/status")
async def obter_status_rpas():
    """Retorna o status de todos os RPAs"""
    try:
        status_rpas = rpa_service.obter_status_todos_rpas()
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "rpas": status_rpas
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status dos RPAs: {str(e)}"
        )

@router_principal.post("/rpa/parar/{operadora}")
async def parar_rpa(operadora: str):
    """Para a execução de um RPA específico"""
    try:
        operadora_upper = operadora.upper()
        
        resultado = rpa_service.parar_rpa(operadora_upper)
        
        return {
            "operadora": operadora_upper,
            "status": "parado",
            "mensagem": f"RPA {operadora_upper} parado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao parar RPA: {str(e)}"
        )

@router_principal.get("/dashboard/resumo")
async def obter_resumo_dashboard(db: Session = Depends(obter_db)):
    """Retorna resumo para o dashboard"""
    try:
        total_operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).count()
        total_clientes = db.query(Cliente).filter(Cliente.status_ativo == True).count()
        
        # Contadores por operadora
        clientes_por_operadora = {}
        operadoras = db.query(Operadora).filter(Operadora.status_ativo == True).all()
        
        for operadora in operadoras:
            count = db.query(Cliente).filter(
                Cliente.operadora_id == operadora.id,
                Cliente.status_ativo == True
            ).count()
            clientes_por_operadora[operadora.nome] = count
        
        status_rpas = rpa_service.obter_status_todos_rpas()
        
        return {
            "total_operadoras": total_operadoras,
            "total_clientes": total_clientes,
            "clientes_por_operadora": clientes_por_operadora,
            "status_rpas": status_rpas,
            "ultima_atualizacao": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resumo do dashboard: {str(e)}"
        )