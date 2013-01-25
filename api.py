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

    def get_school(self, school_type, province, district):
        # schooltype:
        # 0 :unkown
        # 1 : famous high school
        # 2 : all high school
        # 3 : all hight scholl with special chois
        # 4 : senior middle school
        # 5 :junior middle scholl
        # 6 : primary school
        # 7 : dazhuan -> high school
        # 8 : zhongzhuan -> senior middle scholl
        start_sch = '''choose_school'''
        end_sch = ''';'''
        re_sch = '''(?<=%s)(.+?)(?=%s)''' % (start_sch, end_sch)
        #re_sch = '''(?<=title=")(.+?)(?=")'''
        #print re_sch
        url = self.api_qq_getschool % (school_type, province, district)
        school_json = json.loads(self.get_http_body(url))
        if school_json['code'] is 0 and school_json['subcode'] is 0:
            schools = {}
            school_html = school_json['result']
            #print school_html
            school_arr = re.findall(re_sch, school_html)
            try:
                for idschool in school_arr:
                    try:
                        school_id = re.findall('''(?<=\()(.+?)(?=,')''', idschool)[0]
                        school_name = re.findall('''(?<=,')(.+?)(?='\))''', idschool)[0]
                        schools[int(school_id)] = school_name
                        try:
                            self.conn.execute("insert into schools(school_type, school_id, school_name, district_id, province_id) values(?,?,?,?,?) ",(school_type, school_id, school_name, district, province))
                        except:
                            continue
                        print '%d%d\t%s\t%d\t%d' % (school_type, int(school_id), school_name, district, province)
                    except:
                        self.log.error("error in province %d district %d idschool %s" % (province, district, idschool))
                        continue
                return schools
            except:
                self.log.error("error in province %d district %d" % (province, district))     
        else:
            return None

    def get_http_body(self, url):
        return urlopen(url).read()

    def main(self):
        self.initialize()

        for school_type in self.school_types:
                for province_id in location.location_array.keys():
                    if province_id < 36:
                        continue
                    for cityid in location.sublocation_array[province_id].keys():
                        district_dict = self.get_district(cityid)
                        if len(district_dict) is 0:
                            continue
                        print district_dict
                        districts = district_dict.keys()

                        for district_id in districts:
                            schools = self.get_school(int(school_type), int(province_id), int(district_id))
                            self.conn.commit()

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
