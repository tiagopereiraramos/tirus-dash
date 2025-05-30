#!/usr/bin/env python3
"""
Sistema RPA BGTELECOM - Inicializador FastAPI
"""
import subprocess
import sys
import os

def main():
    """Executa o servidor FastAPI"""
    print("Iniciando Sistema RPA BGTELECOM - FastAPI Backend")
    
    # Navegar para o diretório backend
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # Executar uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServidor FastAPI finalizado.")
    except Exception as e:
        print(f"Erro ao executar FastAPI: {e}")

if __name__ == "__main__":
    main()