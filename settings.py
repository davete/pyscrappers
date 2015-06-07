#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-

from os.path import dirname,  join,  abspath

DEBUG=True

USER_AGENT_HEADER = {'User-Agent': [
            'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0']}
JSON_DIR = 'json'
DATA_DIR = 'data'
DATETIME_FORMAT = '%Y-%m-%d %H:%M'
KEYWORDS_FILE = 'keywords.txt'

BASE_PATH = dirname(abspath(__file__))
JSON_PATH = join(BASE_PATH,  JSON_DIR)
DATA_PATH = join(BASE_PATH,  DATA_DIR)
KEYWORDS_PATH = join(BASE_PATH,  KEYWORDS_FILE)

SIMPLYHIRED_BASE_URL = 'https://www.simplyhired.com'
SIMPLYHIRED_QUERY_URL = 'https://www.simplyhired.com/search?q=%s'
#several keywords, 50 perpage, order by date
#SIMPLYHIRED_QUERY_URL = 'https://www.simplyhired.com/search?qa=python+twisted&ws=50&sb=dd'
USAJOBS_BASE_URL = 'https://www.usajobs.gov'
USAJOBS_QUERY_URL = 'https://www.usajobs.gov/Search?Keyword=%s&Location=&search=Search&AutoCompleteSelected=False'
# for next page:
#"/Search/GetPageResultsNew?page=2&keyword=software&statusFilter=public"
#advanced search doesn't show fields in the url https://www.usajobs.gov/Search/GetAdvancedSearchResults
