# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BoPipelineItem(scrapy.Item):
    html_response = scrapy.Field()

    entities_nlp_result = scrapy.Field()
    keywords_nlp_result = scrapy.Field()
    concepts_nlp_result = scrapy.Field()
    tags = scrapy.Field()

    sentiment_nlp_result = scrapy.Field()
    category_nlp_result = scrapy.Field()

    def get_url(self):
        return self['html_response'].url


class BoPackagedItem(scrapy.Item):
    url = scrapy.Field()
    language = scrapy.Field()
    category = scrapy.Field()
    doc_sentiment = scrapy.Field()
    tags = scrapy.Field()
