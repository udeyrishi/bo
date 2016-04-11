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

import json
import logging

import pymongo
import time
from scrapy.exceptions import DropItem

from bo.items import BoPackagedItem
from bo.utils import preconditions
from bo.utils.exceptions import BoSettingsError

MONGO_DATABASE = 'MONGO_DATABASE'
MONGO_URI = 'MONGO_URI'
MONGO_COLLECTION_NAME = 'MONGO_COLLECTION_NAME'
OUTPUT_FILE = 'OUTPUT_FILE'


class PackagingStage(object):
    def process_item(self, bo_pipeline_item, spider):
        packaged_item = BoPackagedItem()
        packaged_item.update(
            url=bo_pipeline_item.get_url(),
            language=bo_pipeline_item['sentiment_nlp_result']['language'],
            category=bo_pipeline_item['category_nlp_result']['category'],
            doc_sentiment=self.cleanup_doc_sentiment(bo_pipeline_item['sentiment_nlp_result']['docSentiment']),
            tags=self.__flatten_tags(bo_pipeline_item['tags']),
            metadata=bo_pipeline_item['metadata'],
            parent_url=bo_pipeline_item['parent_url'],
            time_updated=time.time()
        )
        return packaged_item

    @staticmethod
    def cleanup_doc_sentiment(doc_sentiment):
        return {
            'mixed': doc_sentiment['mixed'] == 1 if 'mixed' in doc_sentiment else False,
            'score': float(doc_sentiment['score']),
            'type': doc_sentiment['type']
        }

    @staticmethod
    def __flatten_tags(tags_dict):
        flattened = []
        for tag_name, tag_properties in tags_dict.items():
            tag_properties['tag'] = tag_name
            flattened.append(tag_properties)
        return flattened


class JsonFileWriterStage(object):
    def __init__(self, output_file):
        self.file_name = output_file if output_file is not None else 'default_output.debug.json'
        self.file = None

    @classmethod
    def from_crawler(cls, crawler):
        output_file = crawler.settings.get(OUTPUT_FILE)
        return cls(output_file)

    def open_spider(self, spider):
        self.file = open(self.file_name, 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, packaged_item, spider):
        line = json.dumps(dict(packaged_item), indent=4) + "\n"
        self.file.write(line)
        return packaged_item


class MongoStorageStage(object):
    def __init__(self, mongo_uri, mongo_db, collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        mongo_uri = preconditions.check_not_none_or_whitespace(crawler.settings.get(MONGO_URI), MONGO_URI,
                                                               exception=BoSettingsError)
        mongo_db = preconditions.check_not_none_or_whitespace(crawler.settings.get(MONGO_DATABASE), MONGO_DATABASE,
                                                              exception=BoSettingsError)
        collection_name = preconditions.check_not_none_or_whitespace(crawler.settings.get(MONGO_COLLECTION_NAME),
                                                                     MONGO_COLLECTION_NAME, exception=BoSettingsError)

        return cls(mongo_uri=mongo_uri, mongo_db=mongo_db, collection_name=collection_name)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db][self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collision = self.db.find_one({'url': item['url']})
        if collision is None:
            post_id = self.db.insert(dict(item))
        else:
            self.db.replace_one({'url': item['url']}, dict(item))
            post_id = collision['_id']
            logging.info(
                "URL: '{0}' was already stored in MongoDB at ID: '{1}'. Will be replaced.".format(item['url'], post_id))

        raise DropItem(
                "URL '{0}' successfully crawled and info stored in MongoDB with post ID '{1}'".format(item['url'],
                                                                                                      post_id))
