""" 
	Started 7:19 am May 13, 2020
	

	Web Scraper for Mavvo

	It should accept as parameters a starting URL, a depth (maximum level of links it should go), and a flag that determines whether it should spider page assets or not.
	
	It should be able to detect when it has already downloaded a link; that is, if two pages refer to the same Javascript file, you don't perform two downloads.
	
	If the depth from the starting page is exceeded, the application should consider that its limit and not spider anything further than the depth of that page.
	
	If the page asset flag is off, the application should only spider links contained in <a href>. If it's on, it needs to do page assets too, and this includes URL references contained in CSS files.
	
	This should go without saying, but I'll say it anyway: While it can use any library suitable in the stack you're working with to request URL contents and parse the data contained in them, it CANNOT use libraries or applications designed to recursively download links. It's got to be your own.
	
	It does not actually need to save the resources it downloads anywhere. Just printing or displaying the resource it is downloading, with its size, is sufficient.
"""
import urllib
import datefinder

from datetime import datetime
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as request  # Web client

now = datetime.now()

class Scraper():

    def __init__(self, config):
        print('CONFIGURING SCRAPER')

        self.counter = 1

        # File modification 

        self.config = config['config']

    def start(self):

        print('STARTING SCRIPT')

        parsed_data = {}

        for configuration in self.config:      
            print("(" + str(self.counter) + ")FETCHING : " + configuration['url'])

            config_targets = configuration['targets']
            
            try:
                client = request(configuration['url'])

            except urllib.error.HTTPError as e:
                if e.code == 404 or e.code == 403:

                    print('PAGE DOES NOT EXIST!')
                    continue   
            else:
                pagecontent = client.read()
                client.close()

                # Parse Data
                for data_target in config_targets:

                    # Grab Data
                    if data_target['container']:
                        parsed_data[data_target['container']] = (self.parse(pagecontent, data_target['element'], data_target['target'])).decode("utf-8") 

                    else:
                        print('PAGE COULD NOT BE REACHED OR WAS REDIRECTED')

                    self.counter += 1

        print('ENDED SCRIPT RUN')

        return parsed_data


    def getFileContents(self, fileTarget):
        urls = []

        for line in open(fileTarget, 'r'):
            urls.append(line.strip()) 

        return urls

    
    def parseHTML(self, html, element, target, html_format=False):
        try:
            result = html.find(element, target).prettify().encode('utf8') if html_format else html.find(element, target).getText().encode('utf8')
        
            return result if result and result is not None else ''

        except:
            return ''


    def parse(self, html, element, target):

        html_soup = soup(html, "html.parser")
        target_content = self.parseHTML(html_soup, element, target)
        # variable = self.parseHTML(html_soup, 'div', {"class": "article-content"}, True)
        return target_content


scraper = Scraper({
        'config': [
            {
                'url': 'https://countrymeters.info/en/World',
                'targets': [{
                    'container': 'world_population',
                    'element': 'div',
                    'target': {"id": "cp1"},
                }]
            },
            # {
            #     'url': 'https://www.buybitcoinworldwide.com/how-many-bitcoins-are-there/',
            #     'targets': [
            #         {
            #             'container': 'bitcoins_left',
            #             'element': 'span',
            #             'target': {"id": "bitcoinsleft"},
            #         },
            #         {
            #             'container': 'bitcoins_issued',
            #             'element': 'span',
            #             'target': {"id": "bitcoinsissued"},
            #         },
            #         {
            #             'container': 'bitcoins_per_day',
            #             'element': 'span',
            #             'target': {"id": "btcperday"},
            #         },
            #         {
            #             'container': 'bitcoins_total',
            #             'element': 'span',
            #             'target': {"id": "totalbtc"},
            #         }
            #     ]
            # },
        ]
    })

data = scraper.start()

print(data)
