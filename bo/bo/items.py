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

    def get_url(self):
        return self['html_response'].url
