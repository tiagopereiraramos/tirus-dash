"""
Configuração Celery + Redis para Sistema RPA BGTELECOM
Conforme especificações do manual
"""

import os
from celery import Celery

# Configurações Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# URL do Redis
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

def create_celery_app():
    """
    Cria e configura a aplicação Celery
    """
    app = Celery(
        "bgtelecom_rpa_orquestrador",
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=[
            "backend.services.orquestrador_celery",
            "backend.services.workflow_aprovacao",
            "backend.services.notificacao_service",
            "backend.services.agendamento_service"
        ]
    )
    
    # Configurações avançadas do Celery
    app.conf.update(
        # Serialização
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        
        # Timezone
        timezone="America/Sao_Paulo",
        enable_utc=True,
        
        # Tracking e timeouts
        task_track_started=True,
        task_time_limit=45 * 60,  # 45 minutos máximo por tarefa
        task_soft_time_limit=40 * 60,  # 40 minutos soft limit
        
        # Worker settings
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_disable_rate_limits=False,
        
        # Compressão
        task_compression="gzip",
        result_compression="gzip",
        
        # Retry settings
        task_default_retry_delay=60,  # 1 minuto entre tentativas
        task_max_retries=3,
        
        # Result settings
        result_expires=3600,  # Resultados expiram em 1 hora
        task_result_expires=3600,
        
        # Beat scheduler (para agendamentos)
        beat_scheduler="celery.beat:PersistentScheduler",
        beat_schedule_filename="celerybeat-schedule",
        
        # Logging
        worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
        
        # Routing de filas
        task_routes={
            "backend.services.orquestrador_celery.executar_rpa_download": {"queue": "rpa_download"},
            "backend.services.orquestrador_celery.executar_rpa_upload_sat": {"queue": "rpa_upload"},
            "backend.services.workflow_aprovacao.processar_aprovacao": {"queue": "aprovacao"},
            "backend.services.notificacao_service.enviar_notificacao": {"queue": "notificacao"},
            "backend.services.agendamento_service.executar_agendamento": {"queue": "agendamento"},
        },
        
        # Definição de filas
        task_default_queue="default",
        task_queues={
            "default": {
                "exchange": "default",
                "exchange_type": "direct",
                "routing_key": "default",
            },
            "rpa_download": {
                "exchange": "rpa",
                "exchange_type": "direct", 
                "routing_key": "download",
            },
            "rpa_upload": {
                "exchange": "rpa",
                "exchange_type": "direct",
                "routing_key": "upload", 
            },
            "aprovacao": {
                "exchange": "workflow",
                "exchange_type": "direct",
                "routing_key": "aprovacao",
            },
            "notificacao": {
                "exchange": "comunicacao",
                "exchange_type": "direct",
                "routing_key": "notificacao",
            },
            "agendamento": {
                "exchange": "scheduler",
                "exchange_type": "direct",
                "routing_key": "agendamento",
            },
        }
    )
    
    return app

# Instância global do Celery
celery_app = create_celery_app()