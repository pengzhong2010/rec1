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
sys.path.append(os.path.expanduser('/data/dev/pyspider'))
from util import ItemIDExtractor

from lib.cache import CACHE
from db.datacenter import DBCENTERREAD

class Index(tornado.web.RequestHandler):

    rec_url = 'http://recapi.datagrand.com/relate/'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")

        # pass
        appname = self.get_argument('appname')
        appid = self.get_argument('appid')
        data_url = self.get_argument('url')
        cnt = self.get_argument('cnt')


        #url cache
        data_url_md5=self.cache_key_build(str(appname+appid+data_url), 'url')
        res_json = CACHE.instance().get_local(data_url_md5)
        if res_json:
            self.write(res_json)
            self.finish()
            return


        #get itemid
        itemid_extractor = ItemIDExtractor()
        retcode, itemid = itemid_extractor.extract(appname,
                                                   data_url)
        # print retcode
        # print itemid
        # self.finish()
        if retcode:
        #66
            res = self.res_formate_dict("FAIL", [], '66')
            res_json = json.dumps(res)
            CACHE.instance().set(data_url_md5, res_json, 7200)
            self.write(res_json)
            self.finish()
            return

        rec_get_query_url=self.rec_url+str(appname)+'?itemid='+itemid+'&cnt='+str(cnt)

        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch,
                                          rec_get_query_url )



        # # rec_str = '{"status": "WARN", "errors": {"message": "cnt illegal ,set to 20", "code": -2}, "recdata": [{"itemid": "c41bc01aea03492d27890f09004c7737", "rsn": ""}, {"itemid": "04afd591a784d96080cfc987cd800050", "rsn": ""}, {"itemid": "58585e57794d6fef3f01dc96a894d67d", "rsn": ""}, {"itemid": "146fa524614f230b97e1ec1bb888b440", "rsn": ""}, {"itemid": "97fbfd6fc61da72e4b20df682e408793", "rsn": ""}, {"itemid": "8a312d906721344d0577ae458cf8cf12", "rsn": ""}, {"itemid": "30e92d7e57c180242651cde1eadd3833", "rsn": ""}, {"itemid": "4e1e894be752051a085da475148f9ac0", "rsn": ""}, {"itemid": "139153f44ba17c6e281a324bdd574955", "rsn": ""}, {"itemid": "77343cb006e277e6799bee36d5b5cce4", "rsn": ""}, {"itemid": "2edc204f61fa2912f78dae50dce0508d", "rsn": ""}, {"itemid": "59a9428b043d4c7be43eed2419da289f", "rsn": ""}, {"itemid": "0352c22abb2b5c4dfb3fe4098aed14ec", "rsn": ""}, {"itemid": "c67385784ac3f774b04df5fcb1dd25d1", "rsn": ""}, {"itemid": "a60120c498cf55bacda594122e3345e8", "rsn": ""}, {"itemid": "d6cec483cbfe1c4bfebbeda869d16b7b", "rsn": ""}, {"itemid": "2389cc0e43214306ba25ec1a64e814f8", "rsn": ""}, {"itemid": "7136981f11b3215af37ba91db39f272b", "rsn": ""}, {"itemid": "6d940dd7cff9f379a8c78927444df666", "rsn": ""}, {"itemid": "19cc91d93461208963a909a29b89d7ee", "rsn": ""}], "request_id": "1471512949576753"}'
        # rec_str = '{"status": "WARN", "errors": {"message": "cnt illegal ,set to 20", "code": -2}, "recdata": [{"itemid": "c41bc01aea03492d27890f09004c7737", "rsn": ""}, {"itemid": "04afd591a784d96080cfc987cd800050", "rsn": ""}], "request_id": "1471512949576753"}'
        rec_str=response.body
        rec_dict = json.loads(rec_str)
        rec_status = rec_dict.get('status')

        if (not rec_status) or (rec_status == 'FAIL'):
            #67
            res = self.res_formate_dict("FAIL", [], '67')
            res_json = json.dumps(res)
            CACHE.instance().set(data_url_md5, res_json, 7200)
            self.write(res_json)
            self.finish()
            return

        rec_recdata = rec_dict.get('recdata')

        if (not rec_recdata) or (len(rec_recdata)==0):
            #68
            res = self.res_formate_dict("FAIL", [], '68')
            res_json = json.dumps(res)
            CACHE.instance().set(data_url_md5, res_json, 7200)
            self.write(res_json)
            self.finish()
            return


        rec_items_list=[]
        for i in rec_recdata:
            rec_items_list.append(i['itemid'])

        #select db
        rec_items_dict={}
        db_select_items_list=[]
        #cache
        for i in rec_items_list:
            data_item_md5 = self.cache_key_build(str(i), 'item')
            item_json = CACHE.instance().get_local(data_item_md5)
            if item_json:
                rec_items_dict[i] = json.loads(item_json)
            else:
                rec_items_dict[i]=''
                db_select_items_list.append(i)
        # print "db"
        # print db_select_items_list
        if db_select_items_list:
            db_select_items_str="','".join(db_select_items_list)

            sql = " select * from item_info where appid=%s and itemid in ('%s') " % (int(appid),db_select_items_str)
            # print sql
            ret = DBCENTERREAD.instance().select(sql)
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
                        data_item_md5 = self.cache_key_build(str(itemid_tmp), 'item')
                        CACHE.instance().set(data_item_md5, json.dumps(i), 7200)

        res_list=[]
        for i in rec_items_list:
            if rec_items_dict[i]:
                res_list.append(rec_items_dict[i])


        res=self.res_formate_dict("OK",res_list)
        res_json = json.dumps(res)
        CACHE.instance().set(data_url_md5, res_json, 7200)
        self.write(res_json)
        self.finish()
        return


    def res_formate_dict(self,status,res_list=None,code=None):
        res_dict={}
        res_dict['status']=status

        if status=='FAIL':
            res_dict['errors']={}
            if code == '66':
                res_dict['errors']['code'] = code
                res_dict['errors']['message'] = 'url not exists'
            elif code == '67':
                res_dict['errors']['code']=code
                res_dict['errors']['message'] = 'rec status faild'
            elif code == '68':
                res_dict['errors']['code'] = code
                res_dict['errors']['message'] = 'rec data not exist'

            return res_dict
        elif status=='OK':
            res_dict['rec_data'] = res_list
            return res_dict
        else:
            return {}

    def str_md5(self,str):

        if type(str) is types.StringType:
            m = hashlib.md5()
            m.update(str)
            return m.hexdigest()
        else:
            return ''

    def cache_key_build(self,str,type):
        item_key=''
        if type=='item':
            item_key = 'ITEM' + str
        elif type=='url':
            item_key=self.str_md5(str)
            if item_key:
                item_key='SURL'+item_key

        return item_key






