# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BoPipelineItem(scrapy.Item):
    # HTTP request results
    html_response = scrapy.Field()

    # RelevanceFilter results
    entities_nlp_result = scrapy.Field()
    keywords_nlp_result = scrapy.Field()
    concepts_nlp_result = scrapy.Field()
    tags = scrapy.Field()
    tags_matched = scrapy.Field()

    # OverallSentimentAnalyser
    sentiment_nlp_result = scrapy.Field()

    def get_url(self):
        return self['html_response'].url

    def update_item(self, **kwargs):
        """
        Updates the item with the key value pairs in kwargs.
        :param kwargs: The key value pair arguments to be added to the item.
        :return: self

        >>> item = BoPipelineItem()
        >>> item = item.update_item(html_response = 'http://www.foo.com/')
        >>> item['html_response']
        'http://www.foo.com/'

        >>> try:
        ...     item = item.update_item(random_key = 12)
        ...     False
        ... except KeyError:
        ...     True
        True
        """
        for field, value in kwargs.items():
            self[field] = value
        return self
