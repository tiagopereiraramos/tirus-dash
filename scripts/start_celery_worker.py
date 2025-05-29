#!/usr/bin/env python3
"""
Script para iniciar Celery Worker
Sistema RPA BGTELECOM
"""

import os
import sys
import subprocess

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def start_worker():
    """Inicia o worker Celery com todas as filas"""
    
    print("=== INICIANDO CELERY WORKER ===")
    print("Sistema: RPA BGTELECOM")
    print("Motor de Fila: Celery + Redis")
    print("Filas: rpa_download, rpa_upload, aprovacao, notificacao, agendamento")
    print()
    
    # Comando para iniciar o worker
    cmd = [
        "celery",
        "-A", "backend.config.celery_config.celery_app",
        "worker",
        "--loglevel=info",
        "--queues=rpa_download,rpa_upload,aprovacao,notificacao,agendamento,default",
        "--concurrency=4",
        "--pool=prefork",
        "--hostname=worker@%h"
    ]
    
    try:
        print("Executando comando:")
        print(" ".join(cmd))
        print()
        
        # Executa o worker
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nParando Celery Worker...")
    except Exception as e:
        print(f"Erro ao iniciar worker: {e}")

if __name__ == "__main__":
    start_worker()