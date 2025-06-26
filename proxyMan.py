import os
import logging

from ScrapyProxyCompat.ScrapyProxyCompat import ScrapyProxyController

controller = ScrapyProxyController(
    retry_time=float(os.getenv("RETRY_TIME", default="300.0")),
    retry_count=int(os.getenv("RETRY_COUNT", default="5")),
)


if os.path.exists("/run/secrets/proxy"):
    proxy_file = "/run/secrets/proxy"
else:
    proxy_file = "/usr/src/app/mealie_scraper/proxy.txt"

controller.readProxies(proxy_file)


controller.startProxies()

logging.debug("Created the following proxy addresses: " + str(controller.getProxyAddresses()))

controller.writeProxies("/usr/src/app/mealie_scraper/scrapy-proxy.txt")
