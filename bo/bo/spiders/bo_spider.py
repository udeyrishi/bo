from csv import DictReader
from urlparse import urlparse

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings

from bo.items import BoPipelineItem
from bo.utils.exceptions import BoSettingsError
from bo.utils.sequence_utils import remove_duplicates


class BoSpider(CrawlSpider):
    """
    The main spider for the Bo crawler.
    """
    name = "bo"
    START_URLS_SETTING_NAME = 'START_URLS_FILE'
    allowed_domains = []
    start_urls = []

    # Just extract all the links from the page and queue them up. allowed_domains will block all the external links
    rules = (Rule(LinkExtractor(), follow=True, callback='parse_response'),)
    url_metadata = dict()

    def __init__(self, start_urls_path=None, *args, **kwargs):
        """
        Creates a new instance of BoSpider.
        :param start_urls_path: The path to the CSV files containing the start URLs and nodes (domains).
        :return: The created BoSpider object.
        """
        super(BoSpider, self).__init__(*args, **kwargs)
        self.start_urls_path = start_urls_path
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
                raise BoSettingsError(message)

        with open(self.start_urls_path, 'r') as starting_urls_csv:
            url_reader = DictReader(starting_urls_csv)

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

    # Scrapy has a weird quirk that start_urls aren't treated the same way as other scraped links, and the responses
    # aren't put in pipelines directly by parse_response. So need to use this as a workaround.
    # Source: http://stackoverflow.com/questions/12736257/why-dont-my-scrapy-crawlspider-rules-work
    def parse_start_url(self, response):
        return self.parse_response(response)

    @staticmethod
    def parse_response(response):
        return BoPipelineItem().update_item(html_response=response)
