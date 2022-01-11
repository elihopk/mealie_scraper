import os

from ScrapyProxyCompat.ScrapyProxyCompat import ScrapyProxyController

controller = ScrapyProxyController(
    retry_time=float(os.getenv("RETRY_TIME", default="300.0")),
    retry_count=int(os.getenv("RETRY_COUNT", default="5")),
)

controller.readProxies("/usr/src/app/mealie_scraper/proxy.txt")

controller.startProxies()

controller.writeProxies("/usr/src/app/mealie_scraper/scrapy-proxy.txt")
