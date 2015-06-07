#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
# -*- coding: utf-8 -*-

import logging
from argparse import ArgumentParser

from pyscrappers.usajobs import SiteUsaJobs
from pyscrappers.simplyhired import SiteSimplyHired


logger = logging.getLogger('')
FORMAT = "%(levelname)s: %(name)s - %(module)s - %(filename)s:%(lineno)s - %(funcName)s - %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

DEBUG = True


def main():
    parser = ArgumentParser(description='Web scrape something.')
    parser.add_argument("url",
                        nargs='?',
                        help="url to scrape")
    parser.add_argument('-d','--debug',
                       # FIXME: change when not developing
                       #default=True,
                        action='store_true',
                        help='debug')
    args = parser.parse_args()

    # if args.debug:
    #     DEBUG = True


    sh = SiteSimplyHired()
    sh.do()

    uj = SiteUsaJobs()
    uj.do()


if __name__ == "__main__":
    main()
