import threading
from lib.rec_driver import *
from lib.pyredis import RedisKv

# from lib.pymysql import PyMysql

class CACHE:
	_instance_lock = threading.Lock()

	@staticmethod
	def instance():
		if not hasattr(CACHE, "_instance"):
			with CACHE._instance_lock:
				if not hasattr(CACHE, "_instance"):
					CACHE._instance = RedisKv('localhost', 6379, 0, 'rec', 0)
		return CACHE._instance
