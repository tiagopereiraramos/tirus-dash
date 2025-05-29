#!/usr/bin/env python3
import subprocess
import time
import os
import signal
import sys

def signal_handler(sig, frame):
    print('Parando servidores...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def start_servers():
    # Iniciar o servidor FastAPI na porta 8000
    print("Iniciando servidor FastAPI na porta 8000...")
    fastapi_process = subprocess.Popen([
        "python", "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])
    
    # Aguardar um pouco para o FastAPI iniciar
    time.sleep(3)
    
    # Iniciar o servidor de desenvolvimento do frontend na porta 5000
    print("Iniciando servidor frontend na porta 5000...")
    frontend_process = subprocess.Popen([
        "npm", "run", "dev:frontend"
    ])
    
    try:
        # Manter os processos rodando
        fastapi_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("Parando servidores...")
        fastapi_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    start_servers()