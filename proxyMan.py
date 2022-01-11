from ScrapyProxyCompat.ScrapyProxyCompat import ScrapyProxyController

controller = ScrapyProxyController()

controller.readProxies("/usr/src/app/mealie_scraper/proxy.txt")

controller.startProxies()

controller.writeProxies("/usr/src/app/mealie_scraper/scrapy-proxy.txt")
