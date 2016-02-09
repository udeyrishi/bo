from bo.libs.alchemyapi_python.alchemyapi import AlchemyAPI
from bo.utils import preconditions
from bo.utils.exceptions import BoSettingsError

ALCHEMY_API_KEY = 'ALCHEMY_API_KEY'
KEYWORDS_FILE = 'KEYWORDS_FILE'
KEYWORD_MATCH_THRESHOLD = 'KEYWORD_MATCH_THRESHOLD'
URL_FLAVOUR = 'url'


class AlchemyNLPPipeline(object):
    def __init__(self, alchemy_api_key, keywords_file, keyword_match_threshold):
        self.alchemy_api = AlchemyAPI(alchemy_api_key)
        self.keywords = self.read_keywords(keywords_file)
        self.keyword_match_threshold = keyword_match_threshold

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get(ALCHEMY_API_KEY)
        keywords_file = crawler.settings.get(KEYWORDS_FILE)
        keyword_match_threshold = crawler.settings.get(KEYWORD_MATCH_THRESHOLD)

        preconditions.check_not_none(api_key, ALCHEMY_API_KEY, exception=BoSettingsError)
        preconditions.check_not_none(keywords_file, KEYWORDS_FILE, exception=BoSettingsError)
        preconditions.check_not_none(keyword_match_threshold, KEYWORD_MATCH_THRESHOLD, exception=BoSettingsError)

        return cls(api_key, keywords_file, keyword_match_threshold)

    @staticmethod
    def read_keywords(keywords_file):
        keywords = set()
        with open(keywords_file, 'r') as f:
            for line in f:
                keyword = line.strip()
                if keyword != '':
                    keywords.add(keyword)
        return keywords


class NamedEntitiesFilter(AlchemyNLPPipeline):
    def process_item(self, item, spider):
        request_url = item['html_response'].url
        entities_nlp_result = self.alchemy_api.entities(URL_FLAVOUR, request_url, options={'sentiment': 1})
        entities = {e['text'] for e in entities_nlp_result['entities']}

        item['entities_nlp_result'] = entities_nlp_result
        item['entities_match_count'] = len(entities.intersection(self.keywords))
        return item
