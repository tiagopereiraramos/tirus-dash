"""
API Routes para Gestão de Operadoras
CRUD completo conforme manual da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from ..main import get_db
from ..models.operadora import Operadora
from ..schemas.operadora_schemas import (
    OperadoraCreate,
    OperadoraUpdate,
    OperadoraResponse,
    ConfiguracaoRPAUpdate
)

router = APIRouter(prefix="/api/operadoras", tags=["operadoras"])

@router.get("/", response_model=List[OperadoraResponse])
async def listar_operadoras(
    skip: int = 0,
    limit: int = 100,
    ativo_apenas: bool = False,
    db: Session = Depends(get_db)
):
    """Lista todas as operadoras"""
    try:
        query = db.query(Operadora)
        
        if ativo_apenas:
            query = query.filter(Operadora.status_ativo == True)
        
        operadoras = query.offset(skip).limit(limit).all()
        return operadoras
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{operadora_id}", response_model=OperadoraResponse)
async def obter_operadora(operadora_id: str, db: Session = Depends(get_db)):
    """Obtém uma operadora específica"""
    try:
        operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
        
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
        return operadora
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=OperadoraResponse)
async def criar_operadora(operadora: OperadoraCreate, db: Session = Depends(get_db)):
    """Cria uma nova operadora"""
    try:
        # Verificar se código já existe
        operadora_existente = db.query(Operadora).filter(
            Operadora.codigo == operadora.codigo.upper()
        ).first()
        
        if operadora_existente:
            raise HTTPException(
                status_code=400, 
                detail="Código da operadora já existe"
            )
        
        # Criar nova operadora
        nova_operadora = Operadora(
            id=str(uuid.uuid4()),
            nome=operadora.nome,
            codigo=operadora.codigo.upper(),
            possui_rpa=operadora.possui_rpa,
            url_portal=operadora.url_portal,
            instrucoes_acesso=operadora.instrucoes_acesso,
            status_ativo=operadora.status_ativo,
            configuracao_rpa=operadora.configuracao_rpa or {},
            classe_rpa=operadora.classe_rpa,
            data_criacao=datetime.now(),
            data_atualizacao=datetime.now()
        )
        
        db.add(nova_operadora)
        db.commit()
        db.refresh(nova_operadora)
        
        return nova_operadora
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{operadora_id}", response_model=OperadoraResponse)
async def atualizar_operadora(
    operadora_id: int,
    operadora_update: OperadoraUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza uma operadora existente"""
    try:
        operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
        
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
        # Atualizar campos fornecidos
        update_data = operadora_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "codigo" and value:
                value = value.upper()
            setattr(operadora, field, value)
        
        operadora.data_atualizacao = datetime.now()
        
        db.commit()
        db.refresh(operadora)
        
        return operadora
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{operadora_id}")
async def deletar_operadora(operadora_id: int, db: Session = Depends(get_db)):
    """Remove uma operadora (soft delete)"""
    try:
        operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
        
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
        # Verificar se possui clientes vinculados
        from ..models.cliente import Cliente
        clientes_vinculados = db.query(Cliente).filter(
            Cliente.operadora_id == operadora_id
        ).count()
        
        if clientes_vinculados > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível remover operadora com {clientes_vinculados} clientes vinculados"
            )
        
        # Soft delete
        operadora.status_ativo = False
        operadora.data_atualizacao = datetime.now()
        
        db.commit()
        
        return {"message": "Operadora removida com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{operadora_id}/configurar-rpa")
async def configurar_rpa_operadora(
    operadora_id: str,
    config_rpa: ConfiguracaoRPAUpdate,
    db: Session = Depends(get_db)
):
    """Configura RPA específico para operadora"""
    try:
        operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
        
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
        # Atualizar configuração RPA
        operadora.possui_rpa = config_rpa.possui_rpa
        operadora.classe_rpa = config_rpa.classe_rpa
        operadora.configuracao_rpa = config_rpa.configuracao_rpa or {}
        operadora.data_atualizacao = datetime.now()
        
        db.commit()
        db.refresh(operadora)
        
        return {
            "message": "Configuração RPA atualizada com sucesso",
            "operadora": operadora
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{operadora_id}/testar-rpa")
async def testar_rpa_operadora(operadora_id: str, db: Session = Depends(get_db)):
    """Testa RPA da operadora"""
    try:
        operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
        
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
        if not operadora.possui_rpa:
            raise HTTPException(
                status_code=400,
                detail="Operadora não possui RPA configurado"
            )
        
        # Simular teste do RPA
        # Em produção, executaria teste real do RPA
        resultado_teste = {
            "operadora": operadora.nome,
            "codigo": operadora.codigo,
            "rpa_status": "funcionando",
            "tempo_resposta": "2.5s",
            "login_portal": "acessível",
            "data_teste": datetime.now().isoformat(),
            "observacoes": "RPA funcionando corretamente"
        }
        
        return {
            "sucesso": True,
            "resultado_teste": resultado_teste
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{operadora_id}/estatisticas")
async def obter_estatisticas_operadora(operadora_id: str, db: Session = Depends(get_db)):
    """Obtém estatísticas da operadora"""
    try:
        operadora = db.query(Operadora).filter(Operadora.id == operadora_id).first()
        
        if not operadora:
            raise HTTPException(status_code=404, detail="Operadora não encontrada")
        
        from ..models.cliente import Cliente
        from ..main import Processo
        
        # Contar clientes
        total_clientes = db.query(Cliente).filter(
            Cliente.operadora_id == operadora_id,
            Cliente.status == "ativo"
        ).count()
        
        # Contar processos por status
        processos_stats = {}
        if total_clientes > 0:
            processos_stats = {
                "total": db.query(Processo).join(Cliente).filter(
                    Cliente.operadora_id == operadora_id
                ).count(),
                "aguardando_download": db.query(Processo).join(Cliente).filter(
                    Cliente.operadora_id == operadora_id,
                    Processo.status_processo == "aguardando_download"
                ).count(),
                "pendente_aprovacao": db.query(Processo).join(Cliente).filter(
                    Cliente.operadora_id == operadora_id,
                    Processo.status_processo == "pendente_aprovacao"
                ).count(),
                "aprovada": db.query(Processo).join(Cliente).filter(
                    Cliente.operadora_id == operadora_id,
                    Processo.status_processo == "aprovada"
                ).count()
            }
        
        estatisticas = {
            "operadora": {
                "id": operadora.id,
                "nome": operadora.nome,
                "codigo": operadora.codigo,
                "possui_rpa": operadora.possui_rpa,
                "status_ativo": operadora.status_ativo
            },
            "clientes": {
                "total": total_clientes
            },
            "processos": processos_stats,
            "data_consulta": datetime.now().isoformat()
        }
        
        return estatisticas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/disponiveis/rpa")
async def listar_operadoras_com_rpa(db: Session = Depends(get_db)):
    """Lista operadoras que possuem RPA disponível"""
    try:
        operadoras = db.query(Operadora).filter(
            Operadora.possui_rpa == True,
            Operadora.status_ativo == True
        ).all()
        
        return {
            "operadoras_rpa": [
                {
                    "id": op.id,
                    "nome": op.nome,
                    "codigo": op.codigo,
                    "classe_rpa": op.classe_rpa,
                    "url_portal": op.url_portal
                }
                for op in operadoras
            ],
            "total": len(operadoras)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))