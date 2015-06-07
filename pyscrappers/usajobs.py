#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-

import logging
import bs4

from basescrapper import Item,  Site,  current_datetime,  obtain_domain
from settings import USAJOBS_BASE_URL,  USAJOBS_QUERY_URL 

logger = logging.getLogger('')

def table2attrs(soupitem,  tabletag):
        details = {}
        tables  = soupitem.select(tabletag)
        for table in tables:
            for row in table.find_all('tr'):
                cells = row.find_all('td', limit=2)
                # cells[1].text.strip()
                details[cells[0].stripped_strings.next().replace(':','')] = cells[1].stripped_strings.next()
        logger.debug('table details',  details)
        return details


class ItemUsaJobs(Item):
    # _itemClass = SiteUsaJobs

    def __init__(self,  base_url,  keyword, date_search):
        logger.debug(' - ItemUJ - ')
        super(ItemUsaJobs, self).__init__(base_url,  keyword, date_search)
    
    def set_description(self):
        logger.debug(' - ItemUJ -')
        self.do_item_query()
        if self.html:
            soup = bs4.BeautifulSoup(self.html)
            logger.debug('len soup %s' % len(soup))       
            # description = soup.select('div.description-full')
            self.description = soup.select('div.jobdetail')[0].text
            #<div class="jobdetail" itemscope="" itemtype="http://schema.org/JobPosting">
            #select('table', style="height: 220px; overflow: visible;")
            # FIXME:
            #self.salary = table2attrs(soup, 'div#jobinfo2 > table')['SECURITY CLEARANCE']


class SiteUsaJobs(Site):
    _itemClass = ItemUsaJobs

    def __init__(self):
        self.base_url = USAJOBS_BASE_URL
        self.search_url = USAJOBS_QUERY_URL
#        self.domain = obtain_domain(self.base_url)
        super(SiteUsaJobs, self).__init__()

    def parse_tables(self, soupitem):
        details = {}
        tables  = soupitem.select('table.joaResultsDetailsTable')
        for table in tables:
            for row in table.find_all('tr'):
                cells = row.find_all('td', limit=2)
                # cells[1].text.strip()
                details[cells[0].stripped_strings.next().replace(':','')] = cells[1].stripped_strings.next()
        return details

#    def parse_agency(self, i):
#        # deprecated method
#        agency = None
#        right_table = soupitem.select('table.joaResultsDetailsTable')[1]
#        for tr in right_table.findAll('tr'):
#            for td in tr.findAll('td'):
#                if td.text == u'Agency:':
#                    for sibling in td.next_siblings:
#                        if sibling.name == 'td':
#                            agency = sibling.text
#        return agency

    def create_item(self,  soupitem):
            item = self._itemClass(self.base_url, self.current_keyword, self.date_search)
            item.item_url = self.base_url + soupitem.select('a.jobTitleLink')[0].attrs.get('href')
            item.title = soupitem.select('a.jobTitleLink')[0].text
            details = self.parse_tables(soupitem)
            item.company = details.get('Agency',  '')
            item.locality = details.get('Location(s)',  '')
            # item.region 
            item.short_description = soupitem.select('p.summary')[0].text.strip()
            # item.published = ''
            item.salary = details.get('Salary',  '')
            item.department = details.get('Department',  '')
            # item.clearance = ''
            item.set_description()
            item.create_json()
            return item

    def create_items(self):
        soup = bs4.BeautifulSoup(self.html)
        soupitems = soup.select('div#jobResultNew')    
        logger.debug('Found %s items' % len(soupitems))
        for soupitem in soupitems:
            item = self.create_item(soupitem)
            self.items.append(item)
        self.obtain_next_page(soup)


    def obtain_next_page(self,  soup):
        # FIXME: solve obtained html doesn't contain items. Ajax?
        next = soup.select('a.nextPage')
        if next:
            logger.debug('there are more pages')
            self.do_query_next_page(self.base_url + next[0]['href'])
