#!/bin/bash

# Populate the cache DB
python populateDB.py

if [[ "${PROXY_ENABLE,,}" == "true" ]]
then
    # Run proxy compatibility script
    python proxyCompat.py &

    echo -e "\e[32mSTART:\e[39m Waiting for 10 seconds for proxies to come up"
    # Sleep 10 seconds to allow for changes to proxy file to propogate
    sleep 10s
fi

# Track how many times the crawler has been started
i=0

# Run crawler repeatedly until container is brought down
while true
do
    ((i++))
    echo -e "\e[32mSTART:\e[39m Running Scrapy Crawler \e[34mi=$i\e[39m"
    scrapy crawl recipes
done
