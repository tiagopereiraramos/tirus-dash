#!/usr/bin/env python3
import subprocess
import sys
import os

def run_fastapi():
    """Executa o servidor FastAPI com configuração adequada"""
    try:
        print("Iniciando servidor FastAPI na porta 8000...")
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ]
        
        # Executar o comando
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Mostrar output em tempo real
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
            
        process.wait()
        
    except KeyboardInterrupt:
        print("\nParando servidor...")
        if process:
            process.terminate()
    except Exception as e:
        print(f"Erro ao executar servidor: {e}")

if __name__ == "__main__":
    run_fastapi()