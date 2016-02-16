"""
Copyright 2016 Udey Rishi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import scrapy


class BoPipelineItem(scrapy.Item):
    html_response = scrapy.Field()

    entities_nlp_result = scrapy.Field()
    keywords_nlp_result = scrapy.Field()
    concepts_nlp_result = scrapy.Field()
    tags = scrapy.Field()

    sentiment_nlp_result = scrapy.Field()
    category_nlp_result = scrapy.Field()
    metadata = scrapy.Field()

    def get_url(self):
        return self['html_response'].url


class BoPackagedItem(scrapy.Item):
    url = scrapy.Field()
    language = scrapy.Field()
    category = scrapy.Field()
    doc_sentiment = scrapy.Field()
    tags = scrapy.Field()
    metadata = scrapy.Field()
