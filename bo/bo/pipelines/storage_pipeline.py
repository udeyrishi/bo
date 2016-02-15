import json

from bo.items import BoPackagedItem

OUTPUT_FILE = 'OUTPUT_FILE'


class PackagingPipeline(object):
    def process_item(self, bo_pipeline_item, spider):
        packaged_item = BoPackagedItem()
        packaged_item['url'] = bo_pipeline_item.get_url()
        packaged_item['language'] = bo_pipeline_item['sentiment_nlp_result']['language']
        packaged_item['category'] = bo_pipeline_item['category_nlp_result']['category']
        packaged_item['doc_sentiment'] = self.cleanup_doc_sentiment(
                bo_pipeline_item['sentiment_nlp_result']['docSentiment'])
        packaged_item['tags'] = bo_pipeline_item['tags']

        return packaged_item

    @staticmethod
    def cleanup_doc_sentiment(doc_sentiment):
        return {
            'mixed': doc_sentiment['mixed'] == 1,
            'score': float(doc_sentiment['score']),
            'type': doc_sentiment['type']
        }


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

