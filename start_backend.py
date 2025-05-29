#!/usr/bin/env python3
"""
Script para iniciar o backend FastAPI seguindo rigorosamente o manual da BGTELECOM
Sistema de Orquestração RPA - Backend completo implementado
"""

import subprocess
import sys
import os

def start_backend():
    """Inicia o backend FastAPI na porta 8000"""
    try:
        # Navegar para o diretório backend
        os.chdir('backend')
        
        # Iniciar o servidor FastAPI
        print("🚀 Iniciando backend FastAPI na porta 8000...")
        print("📋 Sistema implementado seguindo rigorosamente o manual da BGTELECOM")
        print("📊 Dados reais: RICAL, ALVORADA, CENZE, FINANCIAL, etc.")
        print("🏢 Operadoras: EMBRATEL, DIGITALNET, AZUTON, VIVO, OI, SAT")
        print("=" * 60)
        
        # Executar o servidor
        subprocess.run([sys.executable, "main.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Backend interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_backend()