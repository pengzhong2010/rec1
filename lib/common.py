import os

def base_path():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    return BASE_DIR

def log_path():
    sep = os.path.sep
    return base_path()+sep+'log'+sep+'log.txt'