#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-

import logging
from os.path import join,  exists,  getmtime
import requests
import json
import string
from datetime import datetime,  timedelta

from settings import *


logger = logging.getLogger('')

# https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

def obtain_domain(url):
    return url.split('/')[2]
    
def obtain_base_url(url):
    base_url = '/'.join(url.split('/')[:3])

def valid_filename(text):
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    return  ''.join(c for c in text if c in valid_chars)

def current_datetime():
    return datetime.now().strftime(DATETIME_FORMAT)

def datetimestr2datetime(datetimestr):
    return datetime.strptime(datetimestr, DATETIME_FORMAT)

def datetime2datetimestr(dt):
    return dt.strftime(DATETIME_FORMAT)

def timeago2datetimestr(datetimestr,  timeago):
    timeagolist = timeago.split()
    logger.debug('%s %s' % (timeagolist[1],  timeagolist[0]))
    if timeagolist[1] == 'days' or 'day':
        td = timedelta(days=int(timeagolist[0].split('+')[0]))
    if timeagolist[1] == 'hours':
        td = timedelta(hours=int(timeagolist[0]))
    delta = datetimestr2datetime(datetimestr)  - td
    return datetime2datetimestr(delta)

def obtain_keywords():
    with open(KEYWORDS_FILE) as f:
        keywordsstr = f.read()
    return keywordsstr.split()

def request_url(url):
    response = requests.get(url, headers=USER_AGENT_HEADER)
    if response.status_code == 200:
        return response.text
    else:
        logger.debug('response status %s' % response.status_code)
    return ''

def datetimestrfromfilepath(filepath):
    try:
        mtime = getmtime(filepath)
    except OSError:
        return ''
    return datetime2datetimestr(datetime.fromtimestamp(mtime))


class Item(object):
    def __init__(self,  base_url,  keyword, date_search):
        logger.debug(' - Item - ')
        self.base_url = base_url
        # attributes to include in json
        self.keyword = keyword
        self.date_search = date_search
        self.item_url = ''
        self.title = ''
        self.company = ''
        self.department = ''
        self.locality = ''
        self.region = ''
        self.short_description = ''
        self.published = ''
        self.salary = ''
        self.clearance = ''
        # requires visiting the item url
        self.description = ''
        # attributes not to include in json
        self.json = ''
        self.json_filepath = ''
        self.html_filepath = ''
        self.html = ''

    def set_attrs(self, *args, **kwargs):
        for dictionary in args:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_json(self):
        logger.debug(' - Item - ')
        d = self.__dict__
        # FIXME: remove these attributes from json, not the dictionary, 
        # cause they get removed from the object
        # d.pop('base_url',  None)
        # d.pop('json',  None)
        # d.pop('json_filepath',  None)
        # d.pop('html_filepath',  None)
        # d.pop('html', None)
        self.json = json.dumps(d, indent=2)

    def set_json_filepath(self):
        self.json_filepath = join(
                                JSON_PATH, "%s_%s_%s_%s_%s.%s" % \
                                (obtain_domain(self.base_url), 
                                self.keyword,
                                valid_filename(self.title), 
                                valid_filename(self.company), 
                                self.region, 
                                'json'
                                )
                            )
        logger.debug(' - Item - ' + self.json_filepath)

    def write_json(self):
        # logger.debug(self.__dict__.keys())
        logger.debug(' - Item - writing: %s' % self.json_filepath)
        with open(self.json_filepath, 'w') as f:
            f.write(self.json)

    def create_json(self):
        logger.debug(' - Item - ')
        self.set_json_filepath()
        self.set_json()
        self.write_json()

    def set_html_filepath(self):
        logger.debug(' - Item - ')
        self.html_filepath = join(
                                DATA_PATH, "%s_%s_%s_%s_%s.%s" % \
                                (obtain_domain(self.base_url), 
                                self.keyword,
                                valid_filename(self.title), 
                                valid_filename(self.company), 
                                self.region, 
                                'html'
                                )
                            )   

    def read_html_filepath(self):
        if exists(self.html_filepath):
            logger.debug(' - Item - reading %s' % self.html_filepath)
            with open(self.html_filepath, 'r') as f:
                data = f.read()
            self.html = data
            logger.debug(' - Item - read data len %s' % len(self.html))
        else:
            self.html = ''

    def write_html_filepath(self):
        logger.debug(' - Item - writing %s' % self.html_filepath)
        with open(self.html_filepath, 'w') as f:
            try:
                f.write(self.html)
            except UnicodeEncodeError:
                f.write(self.html.encode('utf-8'))
                logger.debug(' - Item - len data encoded %s' % len(self.html.encode('utf-8')))

    def request_item_url(self):
        logger.debug(' - Item - requesting %s' % self.item_url)
        # some items may redirect to a different domain, that will have different parsing
        self.html = request_url(self.item_url)
        logger.debug(' - Item - requested data len %s' % len(self.html))

    def obtain_item_html(self):
        logger.debug(' - Item - obtaining data')
        if DEBUG:
            self.read_html_filepath()
            if self.html:
                return
        self.request_item_url()
        if DEBUG:
            self.write_html_filepath()

    def do_item_query(self):
        logger.debug(' - Item - ')
        self.set_html_filepath()
        self.obtain_item_html()
            
    def set_description(self):
        pass

class Site(object):
    def __init__(self):
        logger.debug(' - Site - ')
        # attributes initialized in the child class
        # logger.debug('in Site.__init__')
        # self.base_url = ''
        # logger.debug(self.base_url)
        # self.search_url = ''
        # self.domain = ''
        self.domain = obtain_domain(self.base_url)
        self.keywords = obtain_keywords()
        
        self.items = []
        self.page_counter = 1
        
        # attributes specific to a search
        self.current_query_url = ''
        self.current_keyword = ''
        self.html_filepath = ''
        self.html = ''
        self.date_search =''

    def set_current_keyword(self, keyword):
        self.current_keyword = keyword
        
    def set_current_query_url(self):
        self.current_query_url = self.search_url % self.current_keyword

    def set_html_filepath(self):
        logger.debug(' - Site - ')
        self.html_filepath = join(
                             DATA_PATH, '%s_%s_%s.html' % \
                             (self.domain, 
                             self.current_keyword, 
                             self.page_counter)
                             )

    def read_html_filepath(self):
        if exists(self.html_filepath):
            logger.debug('reading %s' % self.html_filepath)
            with open(self.html_filepath, 'r') as f:
                data = f.read()
            self.html = data
            self.date_search =  datetimestrfromfilepath(self.html_filepath)
            logger.debug(' - Site - read data len %s' % len(self.html))
        else:
            self.html = ''
            self.date_search = ''

    def write_html_filepath(self):
        with open(self.html_filepath, 'w') as f:
            try:
                f.write(self.html)
            except UnicodeEncodeError:
                f.write(self.html.encode('utf-8'))
                logger.debug(' - Site - len data encoded %s' % len(self.html.encode('utf-8')))

    def request_query_url(self):
        logger.debug(' - Site - requesting %s' % self.current_query_url)
        self.html = request_url(self.current_query_url)
        self.date_search = current_datetime()
        logger.debug('requested data len %s' % len(self.html))

    def obtain_query_html(self):
        logger.debug(' - Site - obtaining data')
        if DEBUG:
            self.read_html_filepath()
            if self.html:
                return
        self.request_query_url()
        if DEBUG:
            self.write_html_filepath()

    def do_query_next_page(self,  next_page_url):
        logger.debug('')
        self.current_query_url = next_page_url
        logger.debug(' - Site - next url: %s' % self.current_query_url)
        self.page_counter += 1
        logger.debug(' - Site - page counter: %s' % self.page_counter)
        self.set_html_filepath()
        self.obtain_query_html()
        self.create_items()
        
    def obtain_next_page(self,  soup):
        pass
        
    def create_item(self,  soupitem):
        pass
        
    def create_items(self):
        pass
        
    def do_query(self,  keyword):
        logger.debug(' - Site - ')
        # self.html = ''
        self.set_current_keyword(keyword)
        self.set_current_query_url()
        self.set_html_filepath()
        self.obtain_query_html()
        self.create_items()

    def do(self):
        logger.debug(' - Site - ')
        for keyword in self.keywords:
            self.do_query(keyword)
