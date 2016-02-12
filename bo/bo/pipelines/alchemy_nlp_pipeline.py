from scrapy.exceptions import DropItem

from bo.libs.alchemyapi_python.alchemyapi import AlchemyAPI
from bo.utils import preconditions
from bo.utils.exceptions import BoSettingsError
from bo.utils.sequence_utils import break_string_sequence_to_words

ALCHEMY_API_KEY = 'ALCHEMY_API_KEY'
TAGS_FILE = 'TAGS_FILE'
TAG_MATCH_THRESHOLD = 'TAG_MATCH_THRESHOLD'
RELEVANCE_THRESHOLD = 'RELEVANCE_THRESHOLD'
URL_FLAVOUR = 'url'


class AlchemyNLPPipeline(object):
    def __init__(self, alchemy_api_key, tags_file, tag_match_threshold, relevance_threshold):
        self.alchemy_api = AlchemyAPI(alchemy_api_key)
        self.tags = break_string_sequence_to_words(self.read_tags_from_file(tags_file))
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
                if tag is not '':
                    tags.add(tag)
        return tags


class RelevanceFilter(AlchemyNLPPipeline):
    def process_item(self, web_page_item, spider):
        entities_nlp_result, keywords_nlp_result, concepts_nlp_result = self.do_nlp(web_page_item)

        relevant_entities = self.extract_relevant_items('entities', entities_nlp_result)
        relevant_keywords = self.extract_relevant_items('keywords', keywords_nlp_result)
        relevant_concepts = self.extract_relevant_items('concepts', concepts_nlp_result)

        tags = relevant_entities.union(relevant_keywords, relevant_concepts)
        tags_matched = tags.intersection(self.tags)

        if len(tags_matched) < self.tag_match_threshold:
            raise DropItem("Dropping page '{0}' because tag match count = {1} < threshold = {2}"
                           .format(web_page_item.get_url(), len(tags_matched), self.tag_match_threshold))

        return web_page_item.update_item(entities_nlp_result=entities_nlp_result,
                                         concepts_nlp_result=concepts_nlp_result,
                                         keywords_nlp_result=keywords_nlp_result,
                                         tags=tags,
                                         tags_matched=tags_matched)

    def extract_relevant_items(self, api_name, api_response):
        return break_string_sequence_to_words({e['text'] for e in api_response[api_name] if
                                               float(e['relevance']) >= self.relevance_threshold})

    def do_nlp(self, item):
        entities_nlp_result = self.alchemy_api.entities(URL_FLAVOUR, item.get_url(), options={'sentiment': 1})
        keywords_nlp_result = self.alchemy_api.keywords(URL_FLAVOUR, item.get_url(), options={'sentiment': 1})
        concepts_nlp_result = self.alchemy_api.concepts(URL_FLAVOUR, item.get_url())
        return entities_nlp_result, keywords_nlp_result, concepts_nlp_result
