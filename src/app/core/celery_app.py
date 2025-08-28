from celery import Celery
from src.app.core.config import settings
from celery.signals import on_after_configure
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
]


# --- THIS IS THE NEW, ROBUST FIX ---
@on_after_configure.connect
def load_all_sql_models(sender, **kwargs):
    """
    Signal handler to import all SQLModel classes when the worker starts.
    This is crucial for ensuring SQLAlchemy's mappers are configured
    correctly before any task that uses the database is executed.
    """
    # By importing here, we guarantee that all models are loaded into Python's
    # memory in the worker process, making them known to SQLAlchemy.
    from src.app import models  # noqa

# ------------------------------------