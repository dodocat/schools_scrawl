#coding=utf-8

import json
import re
import sqlite3
import logging
import os
import os.path as path
from urllib import urlopen
from location import location

import sys

class SchoolCrawler:

    #school_types = [6, 5, 4, 2]
    school_types = [4]
    db = 'result.db'
    api_qq_getdistrict = '''http://api.pengyou.com/json.php?\
                            mod=getdistrict\
                            &cityid=%d\
                            &district_obj_name=_distinct&g_tk=861588235'''
    api_qq_getschool = '''http://api.pengyou.com/json.php?\
                            mod=school&act=selector\
                            &schooltype=%d\
                            &country=0\
                            &province=%d\
                            &district=%d\
                            &g_tk=861588235'''

    def get_district(self, cityid):
        url = self.api_qq_getdistrict % cityid
        dists_json = json.loads(self.get_http_body(url))
        if dists_json['code'] is 0 and dists_json['subcode'] is 0:
            district_arr = dists_json['result']['district_arr']
            return district_arr

    def get_http_body(self, url):
        return urlopen(url).read()

    def main(self):
        self.initialize()


        for province_id in location.location_array.keys():
            print "province: %s     province_id: %d" %(location.location_array[province_id], province_id)
            for cityid in location.sublocation_array[province_id].keys():
                print "\t city: %s \t city_id: %d" %(location.sublocation_array[province_id][cityid], cityid)
                district_dict = self.get_district(cityid)
                if len(district_dict) is 0:
                    continue
                districts = district_dict.keys()
                for district_id in districts:
                    print'\t\t district: %s \t district_id: %d' %(district_dict[district_id], int(district_id))


    def initialize(self):
        if path.exists(self.db):
            self.conn = sqlite3.connect(self.db)
        else:
            self.create_table()
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.commit()

        logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.DEBUG)
        self.log = logging.getLogger('root.test')
        log = self.log
        log.setLevel(logging.WARN) #日志记录级别为WARNNING  
        log.info('info') #不会被记录  
        log.debug('debug') #不会被记录  
        log.warning('warnning') 
        log.error('error')


    def finalize(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def create_table(self):
        self.conn = sqlite3.connect(self.db)
        self.conn.execute("create table schools( \
                id integer primary key autoincrement,\
                school_type int not null,\
                school_id int unique not null,\
                school_name varchar(200) not null,\
                district_id int not null,\
                province_id int not null)"
            )
        self.conn.commit()

SchoolCrawler().main()
