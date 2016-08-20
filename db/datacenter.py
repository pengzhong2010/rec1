import threading
from lib.rec_driver import *
# from lib.pyredis import RedisKv

from lib.pymysql import PyMysql

class DBCENTERREAD:
	_instance_lock = threading.Lock()

	@staticmethod
	def instance():
		if not hasattr(DBCENTERREAD, "_instance"):
			with DBCENTERREAD._instance_lock:
				if not hasattr(DBCENTERREAD, "_instance"):
					DBCENTERREAD._instance = PyMysql("rr-2zeq53lf7562ks1ko.mysql.rds.aliyuncs.com", 3306, "siterec", "siterec123456",
                                 "siterec_datacenter")
		return DBCENTERREAD._instance