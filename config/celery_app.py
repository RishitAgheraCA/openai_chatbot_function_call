# import os

# from celery import Celery
# from config.settings.conf import app_config

# # set the default Django settings module for the 'celery' program.
# DJANGO_SETTINGS_MODULE = app_config.DJANGO_SETTINGS_MODULE
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

# from django.conf import settings

# app = Celery(settings.APP_NAME)

# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# # - namespace='CELERY' means all celery-related configuration keys
# #   should have a `CELERY_` prefix.
# app.config_from_object("django.conf:settings", namespace="CELERY")

# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()
