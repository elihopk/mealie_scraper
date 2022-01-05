from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import populateDB
from mealie_scraper.spiders.recipes_spider import RecipesSpider

populateDB.initDB()


def startCrawler():
    process = CrawlerProcess(get_project_settings())
    process.crawl(RecipesSpider)
    process.start()
    callbackCrawler()


def callbackCrawler():
    startCrawler()


startCrawler()
