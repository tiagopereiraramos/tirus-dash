#!/usr/bin/env python3
"""
Inicializador exclusivo do Sistema RPA BGTELECOM
Backend: FastAPI na porta 8000
Frontend: Vite na porta 3000
Express: COMPLETAMENTE REMOVIDO
"""

import subprocess
import sys
import time
import os

def start_backend():
    """Inicia o backend FastAPI na porta 8000"""
    print("🚀 Iniciando Backend FastAPI na porta 8000...")
    backend_process = subprocess.Popen([
        sys.executable, "backend_fastapi_completo.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return backend_process

def start_frontend():
    """Inicia o frontend Vite na porta 3000"""
    print("🌐 Iniciando Frontend Vite na porta 3000...")
    frontend_process = subprocess.Popen([
        "npx", "vite", "--host", "0.0.0.0", "--port", "3000"
    ], cwd="client", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return frontend_process

def main():
    try:
        print("=" * 60)
        print("🎯 SISTEMA RPA BGTELECOM - INICIALIZAÇÃO EXCLUSIVA FASTAPI")
        print("=" * 60)
        print("✅ Express REMOVIDO")
        print("✅ Backend: FastAPI (Python)")
        print("✅ Frontend: Vite + React")
        print("=" * 60)
        
        # Iniciar backend FastAPI
        backend = start_backend()
        time.sleep(5)  # Aguardar backend inicializar
        
        # Iniciar frontend Vite
        frontend = start_frontend()
        
        print("\n🎉 Sistema iniciado com sucesso!")
        print("📊 Backend FastAPI: http://localhost:8000")
        print("📖 Documentação API: http://localhost:8000/docs")
        print("🌐 Frontend React: http://localhost:3000")
        print("\n⏹️  Pressione Ctrl+C para parar o sistema")
        
        # Aguardar interrupção
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Parando o sistema...")
            backend.terminate()
            frontend.terminate()
            print("✅ Sistema parado com sucesso")
            
    except Exception as e:
        print(f"❌ Erro ao iniciar o sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()