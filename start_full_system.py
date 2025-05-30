#!/usr/bin/env python3
"""
Sistema RPA BGTELECOM - Inicializador Completo
Inicia o backend FastAPI e frontend Vite simultaneamente
"""
import subprocess
import sys
import os
import signal
import threading
import time

def start_backend():
    """Inicia o servidor FastAPI"""
    print("🚀 Iniciando Backend FastAPI...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
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
        print("\n🔴 Backend FastAPI finalizado.")
    except Exception as e:
        print(f"❌ Erro ao executar FastAPI: {e}")

def start_frontend():
    """Inicia o servidor Vite do frontend"""
    print("⚡ Iniciando Frontend Vite...")
    time.sleep(3)  # Aguarda o backend iniciar
    
    root_dir = os.path.dirname(__file__)
    os.chdir(root_dir)
    
    cmd = ["npm", "run", "dev"]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🔴 Frontend Vite finalizado.")
    except Exception as e:
        print(f"❌ Erro ao executar Vite: {e}")

def main():
    """Executa ambos os servidores simultaneamente"""
    print("🎯 SISTEMA RPA BGTELECOM - INICIALIZAÇÃO COMPLETA")
    print("=" * 50)
    
    # Criar threads para executar ambos os servidores
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    
    try:
        # Iniciar ambos os servidores
        backend_thread.start()
        frontend_thread.start()
        
        # Aguardar indefinidamente
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🔴 Finalizando Sistema RPA BGTELECOM...")
        sys.exit(0)

if __name__ == "__main__":
    main()