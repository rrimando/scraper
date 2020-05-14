#!/usr/bin/python
""" 
    Web Scraper
"""
import re, urllib, threading, queue, argparse, requests

from os import path
from pprint import pprint
from urllib.parse import urlparse
from http.client import InvalidURL
from urllib.error import  URLError
from urllib.request import urlopen as request  # Web client

from requests.exceptions import ConnectionError

class Scraper():

    def __init__(self, config):
        self.counter = 1

        # Request Headers
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
        
        # Configuration
        self.config = config['config']

        # Configuration current iteration
        self.starting_url = ''
        self.download_assets = False
        self.max_depth = 0

        # Shared URLLIB
        self.client = []
        self.request = []
        self.response = []

        # Iteration configuration
        self.resetItemContainer()

        # Queue
        self.queue = queue.Queue()
        self.processed_urls = []

        # Output
        self.output = {}

    def start(self):

        print('STARTING SCRAPER')

        for configuration in self.config:      
            self.starting_url = configuration['starting_url']
            self.download_assets = configuration['download_assets']
            self.max_depth = configuration['max_depth']

            # Process Start URL
            self.processLink(self.starting_url, 1)

        # Create threads to process queue
        try:
            threading.Thread(target=self.processQueue, daemon=True).start()
        except Exception as error:
            print("Error: unable to start thread: ({})".format(error))
        
        # Block till all tasks are done
        self.queue.join()

        print('COMPLETED')
        return self.output

    def processQueue(self):
        while True:
            queue_item = self.queue.get()
            self.processLink(queue_item['url'], queue_item['depth'])
            print('Done')
            self.queue.task_done()

    def resetItemContainer(self):
        self.current_items = {
            'links': [],
            'images': [],
            'javascript': [],
            'stylesheets': [],
        }

    def processLink(self, url, depth=1):

        print("(" + str(self.counter) + ")SCRAPING : " + url)

        self.output[url] = {}

        if depth <= self.max_depth:

            # Fetch Content
            self.client = self.getUrl(url)
            pagecontent = self.client.content
       
            # Get URLs and Links
            urls = self.getLinks(pagecontent)

            for inner_url in urls:
                # Process urls
                self.processUrl(self.filterString(inner_url), depth)

            # Cleanup            
            self.resetItemContainer()

        self.counter += 1
        self.output[url] = self.current_items


    def getLinks(self, content):
        return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(content)) + re.findall(r'src="(.*?)"', str(content)); + re.findall(r'href="(.*?)"', str(content));

    def processUrl(self, url, depth):
        # Identify link type
        if url not in self.processed_urls and url != self.starting_url:
            self.sortLink(url, depth)
            self.processed_urls.append(url)

        pass

    def sortLink(self, url, depth):

        link_type = 'links'

        file_types = {
            'images': ['jpg', 'png', 'gif', 'ico'],
            'javascript': ['js'],
            'stylesheets': ['css', 'scss'],
        }
        # Append protocol and base url
        if '://' not in url:
            delimiter = "" if url[:-1].startswith("/") else "/"
            url = (delimiter).join([self.starting_url, url])
        
        # Parse file extension
        file_ext = (url.split('/')[-1]).split('.')[-1]

        if file_ext:
            for file_type in file_types:
                if file_ext in file_types[file_type]:
                    link_type = file_type
                    break

        # Skip downloading assets if not required
        if not self.download_assets and link_type is not 'links':
            return
        else:
            filesize = self.getFileSize(url)
            
            # Determine if we add the url to queue
            next_depth = depth + 1
            if next_depth <= self.max_depth:
                if link_type not in ['javascript', 'images']:
                    self.queue.put({'url': self.filterString(url), 'depth': next_depth})

            self.current_items[link_type].append(
                {
                    'url': url,
                    'size': "{} KB".format(filesize) if filesize else 'Could not fetch filesize',
                    'depth': depth
                }
            )

    def getFileSize(self, url):
        response = self.getUrl(url, True)
        return response.headers.get('Content-Length') if response else None

    def getUrl(self, url, stream=False):
        try:
            return requests.get(url, stream=True, headers=self.headers) if stream else requests.get(url, headers=self.headers)
        except (ConnectionError, URLError, BlockingIOError, InvalidURL, AttributeError) as error:
            self.handleError(error, url)    

    def handleError(self, url, error):
        if hasattr(error, 'reason'):
            print('We failed to reach a server. URL({}) Reason: {}'.format(url, error.reason))
        elif hasattr(error, 'code'):
            print('The server couldn\'t fulfill the request. URL({}) Error code:'.format(url, error.code))
        else:
            print('Encountered an error. URL({})'.format(url))

        return

    def filterString(self, string):
        return string.strip()

"""
    SCRIPT
"""

parser = argparse.ArgumentParser(description='A simple url scraper')
   
parser.add_argument('--url', required=True)
parser.add_argument('--depth', required=True)
parser.add_argument('--assets', required=True)

args = parser.parse_args()

def urlValidator(url):
    try:
        result = urlparse(url)
        if result.scheme and result.netloc:
            return True
        else:
            return False
    except:
        return False

if urlValidator(args.url):
    scraper = Scraper({
            'config': [
                {
                    'starting_url': args.url,
                    'max_depth': int(args.depth),
                    'download_assets': True if (args.assets) else False,
                }
            ]
        })

    data = scraper.start()
    pprint(data)
else:
    print('Please provide a valid URL')