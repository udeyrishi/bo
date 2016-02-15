from scrapy.exceptions import DropItem

from bo.libs.alchemyapi_python.alchemyapi import AlchemyAPI
from bo.utils import preconditions
from bo.utils.exceptions import BoSettingsError
from bo.utils.sequence_utils import break_string_sequence_to_words, conditional_count

ALCHEMY_API_KEY = 'ALCHEMY_API_KEY'
TAGS_FILE = 'TAGS_FILE'
TAG_MATCH_THRESHOLD = 'TAG_MATCH_THRESHOLD'
RELEVANCE_THRESHOLD = 'RELEVANCE_THRESHOLD'
URL_FLAVOUR = 'url'
TAG_MATCHED_KEY = 'matched'


class AlchemyNLPPipeline(object):
    def __init__(self, alchemy_api_key, tags_file, tag_match_threshold, relevance_threshold):
        self.alchemy_api = AlchemyAPI(alchemy_api_key)
        self.tags = self.read_tags_from_file(tags_file)
        self.tag_match_threshold = tag_match_threshold
        self.relevance_threshold = relevance_threshold

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get(ALCHEMY_API_KEY)
        tags_file = crawler.settings.get(TAGS_FILE)
        tag_match_threshold = crawler.settings.getint(TAG_MATCH_THRESHOLD, default=None)
        relevance_threshold = crawler.settings.getfloat(RELEVANCE_THRESHOLD, default=None)

        preconditions.check_not_none(api_key, ALCHEMY_API_KEY, exception=BoSettingsError)
        preconditions.check_not_none(tags_file, TAGS_FILE, exception=BoSettingsError)
        preconditions.check_not_none(tag_match_threshold, TAG_MATCH_THRESHOLD, exception=BoSettingsError)
        preconditions.check_not_none(relevance_threshold, RELEVANCE_THRESHOLD, exception=BoSettingsError)

        return cls(api_key, tags_file, tag_match_threshold, relevance_threshold)

    @staticmethod
    def read_tags_from_file(tags_file):
        tags = set()
        with open(tags_file, 'r') as f:
            for line in f:
                tag = line.strip()
                if tag != '':
                    tags.add(tag)
        return tags


class NLPPerformer(AlchemyNLPPipeline):
    def process_item(self, bo_pipeline_item, spider):
        entities_nlp_result, keywords_nlp_result, concepts_nlp_result = self.do_nlp(bo_pipeline_item)
        bo_pipeline_item.update(entities_nlp_result=entities_nlp_result,
                                concepts_nlp_result=concepts_nlp_result,
                                keywords_nlp_result=keywords_nlp_result)
        return bo_pipeline_item

    def do_nlp(self, bo_pipeline_item):
        entities_nlp_result = self.alchemy_api.entities(URL_FLAVOUR, bo_pipeline_item.get_url(),
                                                        options={'sentiment': 1})
        keywords_nlp_result = self.alchemy_api.keywords(URL_FLAVOUR, bo_pipeline_item.get_url(),
                                                        options={'sentiment': 1})
        concepts_nlp_result = self.alchemy_api.concepts(URL_FLAVOUR, bo_pipeline_item.get_url())
        return entities_nlp_result, keywords_nlp_result, concepts_nlp_result


class TagAnalyzer(AlchemyNLPPipeline):
    def process_item(self, bo_pipeline_item, spider):
        web_page_tags = self.extract_tags_from_nlp_results(concepts=bo_pipeline_item['concepts_nlp_result'],
                                                           entities=bo_pipeline_item['entities_nlp_result'],
                                                           keywords=bo_pipeline_item['keywords_nlp_result'])
        self.append_matching_status(web_page_tags)
        bo_pipeline_item.update(tags=web_page_tags)
        return bo_pipeline_item

    def append_matching_status(self, web_page_tags):
        leftover = set()
        for tag in web_page_tags:
            if tag in self.tags:
                web_page_tags[tag][TAG_MATCHED_KEY] = 'yes'
            else:
                leftover.add(tag)

        target_tag_words = break_string_sequence_to_words(self.tags)

        for tag in leftover:
            for partial_tag in tag.split():
                if partial_tag in target_tag_words:
                    web_page_tags[tag][TAG_MATCHED_KEY] = 'partial'
                    break
            if TAG_MATCHED_KEY not in web_page_tags[tag]:
                web_page_tags[tag][TAG_MATCHED_KEY] = 'no'

    def extract_tags_from_nlp_results(self, **nlp_result_kwargs):
        # WARNING: This approach will overwrite previously encountered tag name by a later one, if multiple
        # entries in nlp_result_kwargs have tags with same text
        # TODO: Fix above by averaging the collisions
        tags = dict()
        for api_name, nlp_result in nlp_result_kwargs.items():
            tags.update(self.extract_relevant_items(api_name, nlp_result))

        return tags

    def extract_relevant_items(self, api_name, api_response):
        return \
            {e['text']: {
                'count': int(e['count']) if 'count' in e else None,
                'relevance': float(e['relevance']),
                'sentiment': None if 'sentiment' not in e else (
                    0 if e['sentiment']['type'] == 'neutral' else float(e['sentiment']['score'])),
                'mixed': None if 'sentiment' not in e else (
                    False if 'mixed' not in e['sentiment'] else float(e['sentiment']['mixed']) == 1)
            }
             for e in api_response[api_name] if
             float(e['relevance']) >= self.relevance_threshold}


class RelevanceFilter(AlchemyNLPPipeline):
    def process_item(self, bo_pipeline_item, spider):
        tags = bo_pipeline_item['tags']
        match_count = conditional_count(tags, lambda tag: tags[tag][TAG_MATCHED_KEY] != 'no')

        if match_count < self.tag_match_threshold:
            raise DropItem("Dropping page '{0}' because tag match count = {1} < threshold = {2}"
                           .format(bo_pipeline_item.get_url(), match_count, self.tag_match_threshold))

        return bo_pipeline_item


class OverallSentimentAnalyser(AlchemyNLPPipeline):
    def process_item(self, bo_pipeline_item, spider):
        sentiment_nlp_result = self.alchemy_api.sentiment(URL_FLAVOUR, bo_pipeline_item.get_url())
        bo_pipeline_item.update(sentiment_nlp_result=sentiment_nlp_result)
        return bo_pipeline_item
