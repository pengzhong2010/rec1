import threading
from celery import Celery

class LOG:
    _instance_lock = threading.Lock()

    @staticmethod
    def instance():
        if not hasattr(LOG,"_instance"):
            with LOG._instance_lock:
                if not hasattr(LOG,"_instance"):
                    LOG._instance = Celery()
                    LOG._instance.conf.update(
                        BROKER_URL='redis://:rec@localhost:6379/0',
                        CELERY_IMPORTS=('wlog',),
                        CELERY_ROUTES={'wlog.write_log': {'queue': 'wlog'},
                                       # 'worker.error_handler': {'queue': 'error'}
                                       },
                        CELERY_TASK_SERIALIZER='json',
                        CELERY_RESULT_SERIALIZER = 'json',
                        CELERY_ACCEPT_CONTENT = ['json'],
                    )
        return LOG._instance

    @staticmethod
    def ilog(str):
        LOG.instance().send_task('wlog.write_log', args=[str])



