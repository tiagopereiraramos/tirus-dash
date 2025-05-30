#!/usr/bin/env python3
"""
Sistema RPA BGTELECOM - Apenas FastAPI
Sem Express, sem proxy, apenas o backend FastAPI
"""

import subprocess
import sys
import os

def main():
    """Executa apenas o servidor FastAPI"""
    print("🚀 SISTEMA RPA BGTELECOM - APENAS FASTAPI")
    print("==========================================")
    
    # Mudar para o diretório backend
    backend_dir = os.path.join(os.getcwd(), 'backend')
    os.chdir(backend_dir)
    
    # Executar FastAPI diretamente
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n🔴 Sistema finalizado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar FastAPI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()