# coding=utf-8

# Broker 设置 RabbitMQ
BROKER_URL = 'redis://:rec@localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://'

# Tasks 位于 worker.py 中
CELERY_IMPORTS = ('wlog', )

# 默认为1次/秒的任务
# CELERY_ANNOTATIONS = {'logx.divide': {'rate_limit': '1/s'}}

CELERY_ROUTES = {'wlog.write_log': {'queue': 'wlog'},
                 # 'worker.error_handler': {'queue': 'error'}
                 }

# 默认所有格式为 json
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']