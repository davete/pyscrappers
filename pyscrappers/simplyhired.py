#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-

import logging
import bs4

from basescrapper import Item,  Site,  timeago2datetimestr,  current_datetime,  obtain_domain
from settings import SIMPLYHIRED_BASE_URL,  SIMPLYHIRED_QUERY_URL

logger = logging.getLogger('')

class ItemSimplyHired(Item):
    # _itemClass = SiteSimplyhired

    def __init__(self,  base_url,  keyword, date_search):
        logger.debug(' - ItemSH - ')
        super(ItemSimplyHired, self).__init__(base_url,  keyword, date_search)
    
    def set_description(self):
        logger.debug(' - ItemSH -')
        self.do_item_query()
        if self.html:
            soup = bs4.BeautifulSoup(self.html)
            logger.debug('len soup %s' % len(soup))       
            # description = soup.select('div.description-full')
            self.description = soup.select('div.detail')[0].text
            #select('table', style="height: 220px; overflow: visible;")
    
class SiteSimplyHired(Site):
    _itemClass = ItemSimplyHired

    def __init__(self):
        logger.debug(' - SiteSH - ')
        self.base_url = SIMPLYHIRED_BASE_URL
        self.search_url = SIMPLYHIRED_QUERY_URL
        # self.domain = obtain_domain(self.base_url)
        super(SiteSimplyHired, self).__init__()

    def create_item_dict(self,  soupitem):
        d = {}
        d['item_url'] = self.base_url + soupitem.select('a.title')[0].attrs.get('href')
        if soupitem.h4:
            d['title'] = soupitem.select('h2')[0].text.strip()
        if soupitem.find('span', itemprop="addressLocality"):
            d['locality'] = soupitem.find('span', itemprop="addressLocality").text
        if soupitem.find('span', itemprop="addressRegion"):
            d['region'] = soupitem.find('span', itemprop="addressRegion").text
        d['short_description'] = soupitem.find('p', itemprop="description").tex
        d['published'] =  timeago2datetimestr(item.date_search,  soupitem.select('span.ago')[0].text)
        # d['description'] = 
        # d[''] = 
        # item(**d)

    def create_item(self,  soupitem):
        logger.debug(' - SiteSH - ')
        item = self._itemClass(self.base_url, self.current_keyword, self.date_search)
        # item.item_url = self.base_url + soupitem.select('a.title')[0].attrs.get('href')
        item.item_url = [a.attrs.get('href') for a in soupitem.select('div.tools > a') if a.attrs.get('href')][0]
        logger.debug('item url %s' % item.item_url)
        item.title = soupitem.select('h2')[0].text.strip()
        try:
            item.company = soupitem.h4.text
        except AttributeError:
            pass
        #      logger.debug('item: %s has no h4 tag' % i)
        if soupitem.find('span', itemprop="addressLocality"):
            item.locality = soupitem.find('span', itemprop="addressLocality").text
        if soupitem.find('span', itemprop="addressRegion"):
            item.region = soupitem.find('span', itemprop="addressRegion").text
        item.short_description = soupitem.find('p', itemprop="description").text
        item.published = timeago2datetimestr(item.date_search,  soupitem.select('span.ago')[0].text)
        #salary
        #clearance
        #department
        item.set_description()
        # logger.debug(item.__dict__.keys())
        item.create_json()
        return item

    def create_items(self):
        logger.debug(' - SiteSH - ')
        soup = bs4.BeautifulSoup(self.html)
        soupitems = soup.select('div.job')    
        for soupitem in soupitems:
            item = self.create_item(soupitem)
            self.items.append(item)
        self.obtain_next_page(soup)

    def obtain_next_page(self,  soup):
        logger.debug(' - SiteSH - ')
        next = soup.select('a.next')
        if next:
            logger.debug('there are more pages')
            self.do_query_next_page(next[0]['href'])
