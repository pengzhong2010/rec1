from celery import Celery
import os
import time

app = Celery()
app.config_from_object('celeryconfig')

@app.task
def write_log(str):

    time_now=time.strftime('%Y-%m-%d %X',time.localtime(time.time()))

    data_str=time_now+" "+str+"\r\n"
    log_write_path = log_path()
    with open(log_write_path, 'ab') as f:
        f.write(data_str)

def log_path():
    sep = os.path.sep
    return base_path()+sep+'log'+sep+'log.txt'

def base_path():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    return BASE_DIR

