import logging
import subprocess
from os import getenv, stat
from sys import argv
from threading import Thread
from time import sleep

# Thread to handle a single proxy instance
class proxyThread(Thread):
    def __init__(
        self, proxy, localport, group=None, target=None, name=None, args=(), kwargs=None
    ):
        super(proxyThread, self).__init__(group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        self.proxy = proxy
        self.localport = localport

    def run(self):
        # Track number of retries
        i = 0

        # Get info about how to respond to failures from environment variables
        retry_time = float(getenv("PROXY_RETRY_TIME", default="300"))
        retry_count = int(getenv("PROXY_RETRY_COUNT", default="5"))

        # Get proxy string without creds for logging purposes
        proxyNoCreds = self.proxy.split("#")[0]

        # Loop for number of retries
        while i <= retry_count:
            i += 1

            logging.debug(
                "PProxy starting for " + proxyNoCreds + " on try " + str(i) + "."
            )

            # Start a subprocess running the proxy
            ret = subprocess.run(
                "pproxy -l http://:"
                + str(self.localport)
                + ' -r "'
                + self.proxy
                + '"',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                shell=True,
            )

            # This code will only be reached if the subprocess exits
            # Check if this is the last retry
            if i == retry_count + 1:
                logging.warning(
                    "PProxy has exited for the final time for "
                    + proxyNoCreds
                    + " with status code "
                    + str(ret.returncode)
                    + ". Program output as follows:\n"
                    + ret.stdout
                )
            else:
                logging.warning(
                    "PProxy has exited for "
                    + proxyNoCreds
                    + " with status code "
                    + str(ret.returncode)
                    + ". Retrying in "
                    + str(retry_time)
                    + " seconds. Program output as follows:\n"
                    + ret.stdout
                )
                sleep(retry_time)


# Open needed files
scrapyProxyFile = open("/usr/src/app/mealie_scraper/scrapy-proxy.txt", "w")
# TODO: Add documentation about this needing to be mounted as a volume
proxyFile = open("/usr/src/app/mealie_scraper/proxy.txt", "r")

# Keep track of ports to start then add to the httpProxyFile
curPort = 2000

# Loop for each proxy in socks5.txt
for line in proxyFile:
    # Skip line if it's a comment
    if line[0] == "#" or line == "":
        continue

    # Make a new proxy and start it
    proxyThread(proxy=line.strip(), localport=curPort).start()

    # Only need to add a newline at the beginning of the write if the file is not empty
    if curPort == 2000:
        scrapyProxyFile.write("http://127.0.0.1:" + str(curPort))
    else:
        scrapyProxyFile.write("\nhttp://127.0.0.1:" + str(curPort))

    curPort += 1

# Close file resources
scrapyProxyFile.close()
proxyFile.close()
