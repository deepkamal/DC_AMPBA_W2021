import csv
import re
from datetime import datetime

import scrapy
from scrapy.crawler import CrawlerProcess


if __name__ == '__main__':

    class MySpiderClass(scrapy.Spider):
        start_urls = ['https://www.espncricinfo.com/series/icc-cricket-world-cup-2019-1144415/match-results']

        def parse(self,resp):
            for aMatch in resp.css('.match-score-block'):


    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    # Crawling process is assigned the Spider
    process.crawl(MySpiderClass)

    # Crawling begins
    process.start()

