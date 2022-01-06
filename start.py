from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import populateDB
from mealie_scraper.spiders.recipes_spider import RecipesSpider

# Populate the cache DB
populateDB.initDB()

# Callbacks used to ensure that each loop of crawling occurs in a different scope
# This is because you can't restart a CrawlerProcess once it finishes
def startCrawler():
    process = CrawlerProcess(get_project_settings())
    process.crawl(RecipesSpider)
    process.start()
    callbackCrawler()


def callbackCrawler():
    startCrawler()

# Start crawling
startCrawler()
