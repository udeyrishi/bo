import scrapy
import csv
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings
from urlparse import urlparse
from bo.utils.sequence_utils import *


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
        """
        Reads the CSV file containing the starting URLS, and populates the self.start_urls and self.allowed_domains.
        All the URL metadata from the CSV is put into the self.url_metadata.
        Removes the duplicates from these two lists.
        The self.start_urls_path is taken as the path to the CSV file. In case it is None, the attribute
        self.START_URLS_SETTING_NAME in the settings object is used.
        :param settings: The settings object to be used for getting the path to the CSV file, in case
                         self.start_urls_path is None
        :return: None
        """
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

            for row in url_reader:
                if row['Node'] and row['URL']:
                    self.allowed_domains.append(row['Node'])
                    self.start_urls.append(self.add_scheme_if_missing(row['URL'], scheme='http'))
                    self.url_metadata[row['Node']] = row
                elif row['Node']:
                    self.allowed_domains.append(row['Node'])
                    self.start_urls.append(self.add_scheme_if_missing(row['Node'], scheme='http'))
                    self.url_metadata[row['Node']] = row
                elif row['URL']:
                    self.start_urls.append(self.add_scheme_if_missing(row['URL'], scheme='http'))
                    self.logger.warning("URL '{0}' didn't have a 'Node' entry. No changes have been made for the "
                                        "allowed_domains and url_metadata attributes for this URL. The former may"
                                        "prevent scraping of this URL and the latter can reduce the amount of info"
                                        "available post scraping.")
                else:
                    self.logger.warning(
                            "Entry '{0}' does not have a Node or URL value. Skipping this CSV entry".format(row))

            # Using list and not set to preserve the original ordering in the CSV.
            # Only done at boot time, so slowdown shouldn't be an issue
            remove_duplicates(self.start_urls)
            remove_duplicates(self.allowed_domains)

    @staticmethod
    def add_scheme_if_missing(url, scheme='http'):
        """
        Adds the scheme to the url if one is missing.
        :param url: The url to be verified.
        :param scheme: The scheme to be used in case url doesn't have a scheme in it.
        :return: The url with a scheme.
        """
        url_object = urlparse(url)
        if url_object.scheme == '':
            return scheme + '://' + url
        else:
            return url

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
