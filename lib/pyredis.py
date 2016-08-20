#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rec_driver import *


class RedisBase:

    def __init__(self, cache_time):
        # print "redis connect create"
        self.cache_time_ = cache_time
        self.is_cache_ = False
        if cache_time > 0:
            self.is_cache_ = True
            self.cache_info_ = {}
            

    def get(self, key, pos, length):
        cur_time = 0
        cache_key = ""
        if self.is_cache_:
            cur_time = int(time.time())
            cache_key = "_".join([str(key), str(pos), str(length)])
            if self.cache_info_.has_key(cache_key):
                [timestamp, cache_value] = self.cache_info_[cache_key]
                if timestamp + self.cache_time_ >= cur_time:
                    return cache_value
        ret = self.get_local(key, pos, length)
        if self.is_cache_:
            self.cache_info_[cache_key] = [cur_time, ret]
        return ret

    def clear_cache(self):
        self.cache_info = {}


class RedisList(RedisBase):

    def __init__(self, redis_ip, redis_port, redis_no, passwd, cache_time):
        RedisBase.__init__(self, cache_time)
        self._rdb = redis.StrictRedis(
            host=redis_ip, port=redis_port, db=redis_no, password=passwd)
        # ilog_info.info("redis ip: %s, port: %d, db: %d" % (redis_ip, redis_port, redis_no))

    def get_local(self, key, pos=0, length=0):
        return self._rdb.lrange(key, pos, pos + length)

    def set(self, key, value_list, timeout=0):
        tmp_key = key + str(random.randint(0, int(time.time())))
        try:
            self._rdb.delete(tmp_key)
            len_ret = self._rdb.rpush(tmp_key, *value_list)
            if len_ret == len(value_list):
                self._rdb.rename(tmp_key, key)
                if timeout > 0:
                    self._rdb.expire(key, timeout)
        except Exception as e:
            # ilog.error("redis storing error, key: %s, err_msg: %s" % (str(key), repr(e)))
            pass
    def get_len(self, key):
        return self._rdb.llen(key)

    def lpop(self, key):
        return self._rdb.lpop(key)


class RedisUpdate:

    def __init__(self, redis_ip, redis_port, redis_no):
        self._rdb = redis.StrictRedis(
            host=redis_ip, port=redis_port, db=redis_no)

    def rpush_key(self, key, value):
        self._rdb.rpush(key, value)


class RedisSortSet(RedisBase):

    def __init__(self, redis_ip, redis_port, redis_no, cache_time, withscore=False):
        RedisBase.__init__(self, cache_time)
        self._rdb = redis.StrictRedis(
            host=redis_ip, port=redis_port, db=redis_no)
        self.with_score_ = withscore

    def get_local(self, key, pos, length):
        ret = self._rdb.zrevrange(
            key, pos, pos + length, withscores=self.with_score_)
        return ret


class RedisKv(RedisBase):

    def __init__(self, redis_ip, redis_port, redis_no, redis_passwd, cache_time):
        RedisBase.__init__(self, cache_time)
        self._rdb = redis.StrictRedis(
            host=redis_ip, port=redis_port, db=redis_no, password=redis_passwd)

    def get_local(self, key, pos=0, length=0):
        if type(key) == list:
            ret = self._rdb.mget(key)
        else:
            ret = self._rdb.get(key)
        return ret

    def set(self, key, value, timeout=0):
        flag = True
        tmp_key = key + "_TMP"
        try:
            self._rdb.delete(tmp_key)
            self._rdb.set(tmp_key, value)
            self._rdb.rename(tmp_key, key)
            if timeout > 0:
                self._rdb.expire(key, timeout)
        except Exception as e:
            # ilog.error("redis storing error, key: %s, err_msg: %s" % (str(key), repr(e)))
            flag = False
        return flag


def main():
    sr_rdb = RedisList(conf.SITE_USER_REC_HOST, conf.SITE_USER_REC_PORT, conf.SITE_USER_REC_DB, conf.SITE_USER_REC_PASSWD, conf.SITE_USER_REC_CACHE_TIME)
    tkey = "1_10001"
    tlist = []
    tlist.append("%d\3%d\3%s\3%d" % (1, 100, '', 1))
    tlist.append("%d\3%d\3%s\3%d" % (2, 500, '', 2))
    tlist.append("%d\3%d\3%s\3%d" % (3, 1000, '', 3))
    sr_rdb.set(tkey, tlist)

if __name__ == "__main__":
    main()
