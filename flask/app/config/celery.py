from celery import Celery
from app.config.flask import Config

config = Config()
celery = Celery(
    __name__,
    broker_url=config.CELERY_BROKER_URL,
    result_backend=config.CELERY_RESULT_BACKEND,
    beat_schedule=config.CELERY_BEAT_SCHEDULE,
    imports=("app.celery",),
    accept_content=['json'],
    result_serializer='json',
    task_serializer="json",
    enable_utc=True,
)



def configure_celery(app):
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
