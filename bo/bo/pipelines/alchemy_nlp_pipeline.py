from bo.libs.alchemyapi_python.alchemyapi import AlchemyAPI
from bo.utils import preconditions
from bo.utils.exceptions import BoSettingsError
from bo.utils.sequence_utils import break_string_sequence_to_words

ALCHEMY_API_KEY = 'ALCHEMY_API_KEY'
KEYWORDS_FILE = 'KEYWORDS_FILE'
KEYWORD_MATCH_THRESHOLD = 'KEYWORD_MATCH_THRESHOLD'
RELEVANCE_THRESHOLD = 'RELEVANCE_THRESHOLD'
URL_FLAVOUR = 'url'


class AlchemyNLPPipeline(object):
    def __init__(self, alchemy_api_key, keywords_file, keyword_match_threshold, relevance_threshold):
        self.alchemy_api = AlchemyAPI(alchemy_api_key)
        self.keywords = break_string_sequence_to_words(self.read_keywords(keywords_file))
        self.keyword_match_threshold = keyword_match_threshold
        self.relevance_threshold = relevance_threshold

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get(ALCHEMY_API_KEY)
        keywords_file = crawler.settings.get(KEYWORDS_FILE)
        keyword_match_threshold = crawler.settings.getint(KEYWORD_MATCH_THRESHOLD, default=None)
        relevance_threshold = crawler.settings.getfloat(RELEVANCE_THRESHOLD, default=None)

        preconditions.check_not_none(api_key, ALCHEMY_API_KEY, exception=BoSettingsError)
        preconditions.check_not_none(keywords_file, KEYWORDS_FILE, exception=BoSettingsError)
        preconditions.check_not_none(keyword_match_threshold, KEYWORD_MATCH_THRESHOLD, exception=BoSettingsError)
        preconditions.check_not_none(relevance_threshold, RELEVANCE_THRESHOLD, exception=BoSettingsError)

        return cls(api_key, keywords_file, keyword_match_threshold, relevance_threshold)

    @staticmethod
    def read_keywords(keywords_file):
        keywords = set()
        with open(keywords_file, 'r') as f:
            for line in f:
                keyword = line.strip()
                if keyword is not '':
                    keywords.add(keyword)
        return keywords


class RelevanceProcessor(AlchemyNLPPipeline):
    def relevance_parser(self, item, extracted_field_name, api_name, api_func):
        nlp_result = api_func(URL_FLAVOUR, item.get_url(), options={'sentiment': 1})
        relevant_field = break_string_sequence_to_words({i[extracted_field_name] for i in nlp_result[api_name] if
                                                         float(i['relevance']) >= self.relevance_threshold})

        item['{0}_nlp_result'.format(api_name)] = nlp_result
        item['{0}_match_count'.format(api_name)] = len(relevant_field.intersection(self.keywords))
        return item


class NamedEntitiesProcessor(RelevanceProcessor):
    def process_item(self, item, spider):
        return self.relevance_parser(item, extracted_field_name='text', api_name='entities',
                                     api_func=self.alchemy_api.entities)


class KeywordsProcessor(RelevanceProcessor):
    def process_item(self, item, spider):
        return self.relevance_parser(item, extracted_field_name='text', api_name='keywords',
                                     api_func=self.alchemy_api.keywords)
