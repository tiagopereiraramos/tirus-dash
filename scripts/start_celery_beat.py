#!/usr/bin/env python3
"""
Script para iniciar Celery Beat (Scheduler)
Sistema RPA BGTELECOM
"""

import os
import sys
import subprocess

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def start_beat():
    """Inicia o scheduler Celery Beat"""
    
    print("=== INICIANDO CELERY BEAT SCHEDULER ===")
    print("Sistema: RPA BGTELECOM")
    print("Função: Agendamentos automáticos")
    print()
    
    # Comando para iniciar o beat
    cmd = [
        "celery",
        "-A", "backend.config.celery_config.celery_app",
        "beat",
        "--loglevel=info",
        "--schedule=/tmp/celerybeat-schedule",
        "--pidfile=/tmp/celerybeat.pid"
    ]
    
    try:
        print("Executando comando:")
        print(" ".join(cmd))
        print()
        
        # Executa o beat
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nParando Celery Beat...")
    except Exception as e:
        print(f"Erro ao iniciar beat: {e}")

if __name__ == "__main__":
    start_beat()