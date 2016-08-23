# -*- coding:utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen

import urllib
import json
import datetime
import time
import sys
import os
import hashlib
import types

from conf import config
from lib.cache import CACHE
from db.datacenter import DBCENTERREAD
from lib.log import LOG

if not config.DEBUG:
    sys.path.append(os.path.expanduser('/data/dev/pyspider'))
    from util import ItemIDExtractor




def res_formate_dict(status, res_list=None, code=None):
    res_dict = {}
    res_dict['status'] = status

    if status == 'FAIL':
        res_dict['errors'] = {}
        if code == '66':
            res_dict['errors']['code'] = code
            res_dict['errors']['message'] = 'url not exists'
        elif code == '67':
            res_dict['errors']['code'] = code
            res_dict['errors']['message'] = 'rec status faild'
        elif code == '68':
            res_dict['errors']['code'] = code
            res_dict['errors']['message'] = 'rec data not exist'
        elif code == '69':
            res_dict['errors']['code'] = code
            res_dict['errors']['message'] = 'cookie not exists'

        return res_dict
    elif status == 'OK':
        res_dict['rec_data'] = res_list
        return res_dict
    else:
        return {}


def str_md5(str):
    if type(str) is types.StringType:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    else:
        return ''


def cache_key_build(str, type):
    item_key = ''
    if type == 'item':
        item_key = str_md5(str)
        if item_key:
            item_key = 'ITEM' + item_key
    elif type == 'url':
        item_key = str_md5(str)
        if item_key:
            item_key = 'SURL' + item_key

    return item_key


class Index(tornado.web.RequestHandler):

    rec_url = 'http://recapi.datagrand.com/relate/'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        # pass



        appname = self.get_argument('appname')
        appid = self.get_argument('appid')
        data_url = self.get_argument('url')
        cnt = self.get_argument('cnt')

        self.set_header_orgin()

        #url cache
        data_url_md5=cache_key_build(str(appname+appid+data_url+cnt), 'url')
        res_json = CACHE.instance().get_local(data_url_md5)
        if res_json:
            request_path = self.request.path
            request_query = self.request.query
            log_str = ' path:' + str(request_path) + ' query:' + str(request_query) + ' res:' + str(res_json)
            LOG.ilog(log_str)
            self.write(res_json)
            self.finish()
            return

        if not config.DEBUG:
            #get itemid
            itemid_extractor = ItemIDExtractor()
            retcode, itemid = itemid_extractor.extract(appname,
                                                       data_url)

            if retcode:
                #66
                res = res_formate_dict("FAIL", [], '66')
                self.res_write(res, data_url_md5)
                return

            rec_get_query_url=self.rec_url+str(appname)+'?itemid='+itemid+'&cnt='+str(cnt)

            client = tornado.httpclient.AsyncHTTPClient()
            response = yield tornado.gen.Task(client.fetch,
                                              rec_get_query_url )

            rec_str = response.body
        else:
            rec_str = '{"status": "WARN", "errors": {"message": "cnt illegal ,set to 20", "code": -2}, "recdata": [{"itemid": "c41bc01aea03492d27890f09004c7737", "rsn": ""}, {"itemid": "04afd591a784d96080cfc987cd800050", "rsn": ""}], "request_id": "1471512949576753"}'

        rec_dict = json.loads(rec_str)
        rec_status = rec_dict.get('status')

        if (not rec_status) or (rec_status == 'FAIL'):
            #67
            res = res_formate_dict("FAIL", [], '67')
            self.res_write(res, data_url_md5)
            return

        rec_recdata = rec_dict.get('recdata')

        if (not rec_recdata) or (len(rec_recdata)==0):
            #68
            res = res_formate_dict("FAIL", [], '68')
            self.res_write(res, data_url_md5)
            return


        rec_items_list=[]
        for i in rec_recdata:
            rec_items_list.append(i['itemid'])

        #select db
        rec_items_dict={}
        db_select_items_list=[]
        #cache
        for i in rec_items_list:
            data_item_md5 = cache_key_build(str(appid) + str(i), 'item')
            item_json = CACHE.instance().get_local(data_item_md5)
            if item_json:
                rec_items_dict[i] = json.loads(item_json)
            else:
                rec_items_dict[i]=''
                db_select_items_list.append(i)


        if db_select_items_list:
            db_select_items_str = "','".join(db_select_items_list)
            db_select_items_str = "'" + db_select_items_str + "'"

            sql1 = " and itemid in (%s) " % db_select_items_str
            sql = " select * from item_info where appid=%s " + sql1
            # print sql
            ret = DBCENTERREAD.instance().select(sql, 'many', (str(appid),))
            if ret:
                for i in ret:
                    tmp = i.get("other_info")
                    if tmp:
                        tmp2 = json.loads(tmp)
                        i['other_info'] = tmp2
                    tmp=i.get("last_update_time")
                    if tmp:
                        tmp2=tmp.strftime("%Y-%m-%d %H:%M:%S")
                        i['last_update_time']=tmp2
                    tmp = i.get("item_modify_time")
                    if tmp:
                        tmp2 = tmp.strftime("%Y-%m-%d %H:%M:%S")
                        i['item_modify_time'] = tmp2
                    tmp = i.get("create_time")
                    if tmp:
                        tmp2 = tmp.strftime("%Y-%m-%d %H:%M:%S")
                        i['create_time'] = tmp2
                    itemid_tmp = i.get("itemid")
                    if itemid_tmp:
                        rec_items_dict[itemid_tmp]=i
                        # cache
                        data_item_md5 = cache_key_build(str(appid)+str(itemid_tmp), 'item')
                        CACHE.instance().set(data_item_md5, json.dumps(i), config.CACHE_TIME)

        res_list=[]
        for i in rec_items_list:
            if rec_items_dict[i]:
                res_list.append(rec_items_dict[i])


        res=res_formate_dict("OK",res_list)
        self.res_write(res,data_url_md5)
        return





    def res_write(self,res,data_url_md5):
        res_json = json.dumps(res)
        CACHE.instance().set(data_url_md5, res_json, config.CACHE_TIME)
        #log
        request_path=self.request.path
        request_query = self.request.query
        log_str=' path:'+str(request_path)+' query:'+str(request_query)+' res:'+str(res_json)
        LOG.ilog(log_str)
        self.write(res_json)
        self.finish()

    def set_header_orgin(self):
        origin = self.request.headers.get('Origin')
        if origin:
            self.set_header("Access-Control-Allow-Origin", origin)
        else:
            self.set_header("Access-Control-Allow-Origin", "*")

        self.set_header("Access-Control-Allow-Credentials", 'true')
        self.set_header("Access-Control-Allow-Methods", "GET")
        self.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")


class Personalized(tornado.web.RequestHandler):

    rec_url='http://recapi.datagrand.com/personal/'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        # pass

        appname = self.get_argument('appname')
        appid = self.get_argument('appid')
        data_url = self.get_argument('url')
        cnt = self.get_argument('cnt')

        self.set_header_orgin()

        # header = self.request.headers
        # print header
        cookie = self.get_cookie('datagrand_uid')
        if not cookie:
            #69
            res = res_formate_dict("FAIL", [], '69')
            self.res_write(res)
            return
        # print cookie

        if not config.DEBUG:
            # get itemid
            itemid_extractor = ItemIDExtractor()
            retcode, itemid = itemid_extractor.extract(appname,
                                                       data_url)

            if retcode or (not itemid):
                itemid = ''

            cookie=str(cookie)
            cid=urllib.quote(cookie)
            rec_get_query_url=self.rec_url+str(appname)+'?cnt='+str(cnt)+'&cid='+cid+'&itemid='+itemid
            client = tornado.httpclient.AsyncHTTPClient()
            response = yield tornado.gen.Task(client.fetch,
                                              rec_get_query_url )
            rec_str = response.body

        else:
            rec_str = '{\"status\": \"OK\", \"recdata\": [{\"itemid\": \"05f7f3ebf5fb2bc0de08eaccb7e207bd\", \"rsn\": \"\"}, {\"itemid\": \"04afd591a784d96080cfc987cd800050\", \"rsn\": \"\"}, {\"itemid\": \"7136981f11b3215af37ba91db39f272b\", \"rsn\": \"\"}, {\"itemid\": \"19cc91d93461208963a909a29b89d7ee\", \"rsn\": \"\"}, {\"itemid\": \"19e92124f69676349cd6ff6210cd79b1\", \"rsn\": \"\"}, {\"itemid\": \"c5fb89c658e77d9d84805ee5ded7566d\", \"rsn\": \"\"}, {\"itemid\": \"2389cc0e43214306ba25ec1a64e814f8\", \"rsn\": \"\"}, {\"itemid\": \"4e1e894be752051a085da475148f9ac0\", \"rsn\": \"\"}, {\"itemid\": \"eeeac074b30d3afd3afcd01ee94cc9ff\", \"rsn\": \"\"}, {\"itemid\": \"d047c8e12241fc41ac26ad50bc954638\", \"rsn\": \"\"}], \"request_id\": \"1471916927781132\"}'

        rec_dict = json.loads(rec_str)
        rec_status = rec_dict.get('status')

        if (not rec_status) or (rec_status == 'FAIL'):
            # 67
            res = res_formate_dict("FAIL", [], '67')
            self.res_write(res)
            return

        rec_recdata = rec_dict.get('recdata')

        if (not rec_recdata) or (len(rec_recdata) == 0):
            # 68
            res = res_formate_dict("FAIL", [], '68')
            self.res_write(res)
            return

        rec_items_list = []
        for i in rec_recdata:
            rec_items_list.append(i['itemid'])

        # select db
        rec_items_dict = {}
        db_select_items_list = []
        # cache
        for i in rec_items_list:
            data_item_md5 = cache_key_build(str(appid) + str(i), 'item')
            item_json = CACHE.instance().get_local(data_item_md5)
            if item_json:
                rec_items_dict[i] = json.loads(item_json)
            else:
                rec_items_dict[i] = ''
                db_select_items_list.append(i)

        if db_select_items_list:
            db_select_items_str = "','".join(db_select_items_list)
            db_select_items_str = "'"+db_select_items_str+"'"

            sql1 = " and itemid in (%s) " % db_select_items_str
            sql = " select * from item_info where appid=%s "+ sql1
            # print sql
            ret = DBCENTERREAD.instance().select(sql,'many',(str(appid),))
            if ret:
                for i in ret:
                    tmp = i.get("other_info")
                    if tmp:
                        tmp2 = json.loads(tmp)
                        i['other_info'] = tmp2
                    tmp = i.get("last_update_time")
                    if tmp:
                        tmp2 = tmp.strftime("%Y-%m-%d %H:%M:%S")
                        i['last_update_time'] = tmp2
                    tmp = i.get("item_modify_time")
                    if tmp:
                        tmp2 = tmp.strftime("%Y-%m-%d %H:%M:%S")
                        i['item_modify_time'] = tmp2
                    tmp = i.get("create_time")
                    if tmp:
                        tmp2 = tmp.strftime("%Y-%m-%d %H:%M:%S")
                        i['create_time'] = tmp2
                    itemid_tmp = i.get("itemid")
                    if itemid_tmp:
                        rec_items_dict[itemid_tmp] = i
                        # cache
                        data_item_md5 = cache_key_build(str(appid) + str(itemid_tmp), 'item')
                        CACHE.instance().set(data_item_md5, json.dumps(i), config.CACHE_TIME)

        res_list = []
        for i in rec_items_list:
            if rec_items_dict[i]:
                res_list.append(rec_items_dict[i])

        res = res_formate_dict("OK", res_list)
        self.res_write(res)
        return




    def res_write(self, res):
        res_json = json.dumps(res)
        # log
        request_path = self.request.path
        request_query = self.request.query
        request_cookie = self.request.headers.get('Cookie')
        if not request_cookie:
            request_cookie = 'None'
        log_str = ' path:' + str(request_path) + ' query:' + str(request_query) +' cookie:'+str(request_cookie)+ ' res:' + str(res_json)
        LOG.ilog(log_str)
        self.write(res_json)
        self.finish()


    def set_header_orgin(self):
        origin = self.request.headers.get('Origin')
        if origin:
            self.set_header("Access-Control-Allow-Origin", origin)
        else:
            self.set_header("Access-Control-Allow-Origin", "*")

        self.set_header("Access-Control-Allow-Credentials", 'true')
        self.set_header("Access-Control-Allow-Methods", "GET")
        self.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")

