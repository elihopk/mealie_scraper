import os

# Scrapy settings for mealie_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'mealie_scraper'

SPIDER_MODULES = ['mealie_scraper.spiders']
NEWSPIDER_MODULE = 'mealie_scraper.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mealie_scraper (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

LOG_LEVEL = os.getenv("LOGLVL", default="INFO")

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'mealie_scraper.middlewares.MealieScraperSpiderMiddleware': 543,
#}

# Verify that a proxy should be used and enable the appropriate settings if so
if os.getenv("PROXY_ENABLE", default="false").lower() == "true":
    RANDOM_UA_PER_PROXY = True
    # Enable or disable downloader middlewares
    # See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
    DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'rotating_proxies.middlewares.RotatingProxyMiddleware': 582,
        'rotating_proxies.middlewares.BanDetectionMiddleware': 583,
        'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 630,
        'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 640,
    }
else:
    # Enable or disable downloader middlewares
    # See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
    DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 630,
        'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 640,
    }

# See https://github.com/TeamHG-Memex/scrapy-rotating-proxies
ROTATING_PROXY_LIST_PATH = '/usr/src/app/mealie_scraper/scrapy-proxy.txt'

# Set providers for fake user agents
FAKEUSERAGENT_PROVIDERS = [
    'scrapy_fake_useragent.providers.FakerProvider',
    'scrapy_fake_useragent.providers.FixedUserAgentProvider'
]

# This user agent will be used if we fail to generate one
FAKEUSERAGENT_FALLBACK = 'Mozilla/5.0 (Android; Mobile; rv:40.0)'

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'mealie_scraper.pipelines.UnescapeHTML': 100,
    'mealie_scraper.pipelines.AddSlug': 200,
    'mealie_scraper.pipelines.DuplicateCheck': 300,
    'mealie_scraper.pipelines.ParseDurations': 400,
    'mealie_scraper.pipelines.AddItemToMealie': 500,
    'mealie_scraper.pipelines.AddItemToCache': 600,
    'mealie_scraper.pipelines.AddRecipeImage': 700,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
