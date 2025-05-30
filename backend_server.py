#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/api/clientes')
def get_clientes():
    return {
        'sucesso': True,
        'clientes': [
            {
                'id': 1,
                'nome_sat': 'RICAL - RACK INDUSTRIA E COMERCIO LTDA',
                'cnpj': '00.052.488/0001-51',
                'unidade': 'RO',
                'status_ativo': True,
                'operadora_nome': 'EMBRATEL'
            },
            {
                'id': 2,
                'nome_sat': 'ALVORADA COMERCIO E SERVICOS LTDA',
                'cnpj': '00.411.566/0001-06', 
                'unidade': 'MT',
                'status_ativo': True,
                'operadora_nome': 'DIGITALNET'
            },
            {
                'id': 3,
                'nome_sat': 'CENZE TELECOM LTDA',
                'cnpj': '17.064.901/0001-40',
                'unidade': 'RO', 
                'status_ativo': True,
                'operadora_nome': 'VIVO'
            }
        ],
        'total': 3
    }

@app.put('/api/clientes/{cliente_id}')
def update_cliente(cliente_id: int, cliente: dict):
    return {
        'sucesso': True,
        'cliente': {
            'id': cliente_id,
            **cliente
        }
    }

@app.get('/api/operadoras')
def get_operadoras():
    return {
        'sucesso': True,
        'operadoras': [
            {'id': 1, 'nome': 'EMBRATEL', 'codigo': 'EMBRATEL', 'status_ativo': True},
            {'id': 2, 'nome': 'DIGITALNET', 'codigo': 'DIGITALNET', 'status_ativo': True},
            {'id': 3, 'nome': 'VIVO', 'codigo': 'VIVO', 'status_ativo': True},
            {'id': 4, 'nome': 'OI', 'codigo': 'OI', 'status_ativo': True},
            {'id': 5, 'nome': 'SAT', 'codigo': 'SAT', 'status_ativo': True},
            {'id': 6, 'nome': 'AZUTON', 'codigo': 'AZUTON', 'status_ativo': True}
        ],
        'total': 6
    }

if __name__ == "__main__":
    print("Backend FastAPI iniciando na porta 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)