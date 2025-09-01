from celery import Celery
from src.app.core.config import settings
from src.app.models import Bill, User

# Define the Celery application instance.
# We point the broker and backend to the same REDIS_URL from our settings.
celery_app = Celery(
    "src.app.tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    broker_connection_retry_on_startup=True,
)

# Add robust, professional configurations.
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover task modules. Celery will look for a tasks.py file
# in all the apps listed here.
# celery_app.autodiscover_tasks(["src.app.tasks.email_tasks"])
celery_app.conf.imports = [
    "src.app.tasks.email_tasks",
    "src.app.tasks.parsing_tasks",
    "src.app.tasks.estimation_tasks",
]
