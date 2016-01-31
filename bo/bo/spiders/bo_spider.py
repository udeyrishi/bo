import scrapy
import csv
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings


class BoSpider(scrapy.Spider):
    name = "bo"
    START_URLS_SETTING_NAME = 'START_URLS'

    def __init__(self, start_urls_path=None):
        scrapy.Spider.__init__(self)
        self.start_urls_path = start_urls_path
        self.allowed_domains = []
        self.start_urls = []
        self.url_metadata = dict()
        self.__read_start_urls(get_project_settings())

    def __read_start_urls(self, settings):
        if not self.start_urls_path:
            if self.START_URLS_SETTING_NAME in settings.attributes:
                self.start_urls_path = settings.attributes[self.START_URLS_SETTING_NAME].value
            else:
                message = "'{0}' setting not configured and scrapy not started with 'start_urls_path' arg. " \
                          "Failed to start the spider".format(self.START_URLS_SETTING_NAME)
                self.logger.error(message)
                raise CloseSpider(message)

        with open(self.start_urls_path, 'r') as starting_urls_csv:
            url_reader = csv.DictReader(starting_urls_csv)

            _allowed_domains = set()
            _start_urls = set()

            for row in url_reader:
                if row['Node'] and row['URL']:
                    _allowed_domains.add(row['Node'])
                    _start_urls.add(row['URL'])
                    self.url_metadata[row['Node']] = row
                elif row['Node']:
                    _allowed_domains.add(row['Node'])
                    _start_urls.add(row['Node'])
                    self.url_metadata[row['Node']] = row
                elif row['URL']:
                    _start_urls.add(row['URL'])
                    self.logger.warning("URL '{0}' didn't have a 'Node' entry. No changes have been made for the "
                                        "allowed_domains and url_metadata attributes for this URL. The former may"
                                        "prevent scraping of this URL and the latter can reduce the amount of info"
                                        "available post scraping.")
                else:
                    self.logger.warning(
                        "Entry '{0}' does not have a Node or URL value. Skipping this CSV entry".format(row))

            self.start_urls += list(_start_urls)
            self.allowed_domains += list(_allowed_domains)

    def parse(self, response):
        for href in response.css("ul.directory.dir-col > li > a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

    @staticmethod
    def parse_dir_contents(response):
        for sel in response.xpath('//ul/li'):
            item = dict()
            item['title'] = sel.xpath('a/text()').extract()
            item['link'] = sel.xpath('a/@href').extract()
            item['desc'] = sel.xpath('text()').extract()
            yield item
