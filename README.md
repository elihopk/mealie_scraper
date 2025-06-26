# mealie_scraper
Mealie_scraper is a dockerized web scraper written in Python using the [Scrapy](https://scrapy.org/) framework. It is intended to be run in perpetuity alongside an instance of [Mealie](https://hay-kot.github.io/mealie/). As the web scraper runs, it will pull recipe data from every web page on the specified websites. The scraper will wait a specified amount of time then restart once it has finished scraping. This allows the scraper to grab new recipes from the specified sites once they are uploaded.
# Usage
See [docker-compose.yml](docker-compose.yml) for using mealie_scraper in a compose file.

To run the container via CLI:
```
docker run \
    -v './mealie_scraper_dc/proxy.txt':'/usr/src/app/mealie_scraper/proxy.txt' \
    -e PROXY_ENABLE=true \
    -e LOGLVL=DEBUG \
    -e API_TOKEN=<API token goes here> \
    -e API_PATH=http://mealie:80/api \
    -e SEARCH_SITES=https://www.simplyrecipes.com/ \
    -e ALLOWED_DOMAINS=www.simplyrecipes.com \
    ghcr.io/elihopk/mealie_scraper/mealie_scraper:latest
```
The `proxy.txt` volume is mandatory if using rotating proxies and should always be mounted to `/usr/src/app/mealie_scraper/proxy.txt` or loaded via a secret named `proxy`.

The `proxy.txt` file should contain a list of proxies, one per line, in [pproxy](https://pypi.org/project/pproxy/) format:

`[http, socks, ss, ssl, secure (Or a combination of these)]://ip_address:port#username:password`

For example:
```
http+ssl://proxyip.com:2323#Good:Creds
socks5://proxyip.com:2323#Good:Creds
```
# Environment Variables
- ALLOWED_DOMAINS
  - Mandatory
  - A space separated list of domains that are allowed to be accessed by the webscraper. Do not include the protocol in this.
- API_PATH
  - Mandatory
  - A web address that the Mealie API can be accessed at
- API_TOKEN
  - Mandatory (or via `api_token` secret)
  - An API token created by a Mealie user which the scraper will use to access the Mealie API
- LOGLVL
  - Optional
    - Default: INFO
  - The logging level Scrapy should display.
  - Possible Options:
    - CRITICAL
    - ERROR
    - WARNING
    - INFO
    - DEBUG
- PROXY_ENABLE
  - Optional
    - Default: false
  - Determines whether or not to enable proxies using [scrapy-rotating-proxies](https://github.com/TeamHG-Memex/scrapy-rotating-proxies)
- RETRY_COUNT
  - Optional
    - Default: 5
  - The number of times that a failed proxy connection should be retried before allowing the proxy thread to die
- RETRY_TIME
  - Optional
    - Default: 300
  - The amount of time in seconds that failed proxy threads should wait before retrying their connections
- SEARCH_SITES
  - Mandatory
  - A space separated list of web addresses to be used as starting points for the scraper. These should be full addresses including protocols and paths.
- TIME_TO_WAIT
  - Optional
    - Default: 5m
  - The amount of time that the scraper should wait to begin crawling again after finishing crawling. This should be formatted as a number and a suffix with d for days, h for hours, m for minutes, and s for seconds.
# Planned Features
- [ ] Fuzzy Slug Cache Searching
- [ ] Default ALLOWED_DOMAINS = SEARCH_SITES
