""" 
    Started 7:19 am May 13, 2020

    Web Scraper for Mavvo

    DONE It should accept as parameters a starting URL, a depth (maximum level of links it should go), and a flag that determines whether it should spider page assets or not.
    
    It should be able to detect when it has already downloaded a link; that is, if two pages refer to the same Javascript file, you don't perform two downloads.
    
    If the depth from the starting page is exceeded, the application should consider that its limit and not spider anything further than the depth of that page.
    
    If the page asset flag is off, the application should only spider links contained in <a href>. If it's on, it needs to do page assets too, and this includes URL references contained in CSS files.
    
    This should go without saying, but I'll say it anyway: While it can use any library suitable in the stack you're working with to request URL contents and parse the data contained in them, it CANNOT use libraries or applications designed to recursively download links. It's got to be your own.
    
    It does not actually need to save the resources it downloads anywhere. Just printing or displaying the resource it is downloading, with its size, is sufficient.
"""
import re
import time
import urllib
import os.path
import threading
import datefinder

from os import path
from random import random
from datetime import datetime
# from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as request  # Web client

now = datetime.now()

class Scraper():

    def __init__(self, config):
        print('CONFIGURING SCRAPER')

        # Request Configuration = Headers
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

        self.counter = 1

        # Configuration
        self.config = config['config']

        # Configuration current iteration
        self.starting_url = ''
        self.download_assets = False
        self.max_depth = 0

        # Iteration configuration
        self.current_depth = 1
        self.current_items = {
            'links': [],
            'images': [],
            'javascript': [],
            'stylesheets': [],
        }

        # Queue
        self.queue = []
        self.processed_urls = []

        # Output
        self.output = {}


    def start(self):

        print('STARTING SCRIPT')

        for configuration in self.config:      
            self.starting_url = configuration['starting_url']
            self.download_assets = configuration['download_assets']
            self.max_depth = configuration['max_depth']

            self.processLink(self.starting_url, 1)

        """
            Processing Queue
        """
        while len(self.queue):
            sleep_interval = random() * 1 * 10
            print("Waiting for {} seconds".format(sleep_interval))

            time.sleep(sleep_interval)

            queue_item = self.queue.pop()
            self.processLink(queue_item['url'], queue_item['depth'])

        print('ENDED SCRIPT RUN')
        return self.output


    def processLink(self, url, depth=1):

        print("(" + str(self.counter) + ")SCRAPING : " + url)

        self.output[url] = {}

        if depth <= self.max_depth:

            # Fetch Content
            try:
                client = self.getUrl(url)

            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                if e.code == 404 or e.code == 403:

                    print('PAGE DOES NOT EXIST!')

                else:

                    print(e)
            else:
                """
                    Get Initial Page Content
                """
                pagecontent = client.read()
                client.close()

                # Get Page Content
                urls = self.getLinks(pagecontent)

            for inner_url in urls:
            # Process urls
                self.processUrl(inner_url, depth)
                self.counter += 1

        self.output[url] = self.current_items


    def getLinks(self, content):
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(content)) + re.findall(r'src="(.*?)"', str(content)); + re.findall(r'href="(.*?)"', str(content));

    def processUrl(self, url, depth):
        
        # Identify link
        if url not in self.processed_urls and url != self.starting_url:
            self.sortLink(url, depth)
            self.processed_urls.append(url)

        pass

    def sortLink(self, url, depth):

        link_type = 'links'

        file_types = {
            'images': ['jpg', 'png', 'gif'],
            'javascript': ['js'],
            'stylesheets': ['css', 'scss'],
        }
        """
            Append protocol and base url
        """
        if '://' not in url:
            delimiter = "" if url[:-1].startswith("/") else "/"
            url = (delimiter).join([self.starting_url, url])
        """
            Parse file extension
        """
        file_ext = (url.split('/')[-1]).split('.')[-1]

        if file_ext:
            for file_type in file_types:
                if file_ext in file_types[file_type]:
                    link_type = file_type
                    break

        """
            Skip downloading assets
        """
        if not self.download_assets and link_type is not 'links':
            return
        else:
            filesize = self.getFileSize(url)
            """
                Determine if we add the url to queue
            """
            next_depth = depth + 1
            if next_depth <= self.max_depth:
                if link_type not in ['javascript', 'images']:
                    self.queue.append({'url': url, 'depth': next_depth})

            self.current_items[link_type].append(
                {
                    'url': url,
                    'size': "{} KB".format(filesize),
                    'depth': self.current_depth
                }
            )


    def getFileSize(self, url):
        # https://stackoverflow.com/questions/40594817/python-http-how-to-check-file-size-before-downloading-it
        response = self.getUrl(url)        

        return response.headers['content-length']

    def getUrl(self, url):        
        # Bug - Returning None for some assets
        request = urllib.request.Request(url, data=None, headers=self.headers)
        response = urllib.request.urlopen(request)

        # response.close()

        return response


scraper = Scraper({
        'config': [
            {
                'starting_url': 'https://btcperperson.com',
                'max_depth': 3,
                'download_assets': True,
            }
        ]
    })

data = scraper.start()

from pprint import pprint
pprint(data)