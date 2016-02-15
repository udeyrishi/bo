from bo.items import BoPackagedItem


class PackagingPipeline(object):
    def process_item(self, bo_pipeline_item, spider):
        packaged_item = BoPackagedItem()
        packaged_item['url'] = bo_pipeline_item.get_url()
        packaged_item['language'] = bo_pipeline_item['sentiment_nlp_result']['language']
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
