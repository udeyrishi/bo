import datetime
import logging

import pause
from scrapy.exceptions import DropItem

from bo.libs.alchemyapi_python.alchemyapi import AlchemyAPI
from bo.utils import preconditions
from bo.utils.exceptions import BoSettingsError
from bo.utils.sequence_utils import break_string_sequence_to_words, conditional_count

ALCHEMY_API_KEY = 'ALCHEMY_API_KEY'
TAGS_FILE = 'TAGS_FILE'
TAG_MATCH_THRESHOLD = 'TAG_MATCH_THRESHOLD'
RELEVANCE_THRESHOLD = 'RELEVANCE_THRESHOLD'
ALCHEMY_API_RETRY_DELAY_MINUTES = 'ALCHEMY_API_RETRY_DELAY_MINUTES'
CASE_INSENSITIVE_TAGS = 'CASE_INSENSITIVE_TAGS'
URL_FLAVOUR = 'url'
TAG_MATCHED_KEY = 'matched'


class AlchemyNLPStage(object):
    def __init__(self, alchemy_api_key, tags_file, tag_match_threshold, case_insensitive_tags, relevance_threshold,
                 api_retry_delay_minutes):
        self.alchemy_api = AlchemyAPI(alchemy_api_key)
        self.case_insensitive_tags = case_insensitive_tags
        self.tags = self.read_tags_from_file(tags_file)
        self.tag_match_threshold = tag_match_threshold
        self.relevance_threshold = relevance_threshold
        self.api_retry_delay_minutes = api_retry_delay_minutes

    @classmethod
    def from_crawler(cls, crawler):
        api_key = crawler.settings.get(ALCHEMY_API_KEY)
        tags_file = crawler.settings.get(TAGS_FILE)
        tag_match_threshold = crawler.settings.getint(TAG_MATCH_THRESHOLD, default=None)
        relevance_threshold = crawler.settings.getfloat(RELEVANCE_THRESHOLD, default=None)
        api_retry_delay_minutes = crawler.settings.getint(ALCHEMY_API_RETRY_DELAY_MINUTES, default=None)
        case_insensitive_tags = crawler.settings.getbool(CASE_INSENSITIVE_TAGS, default=None)

        preconditions.check_not_none_or_whitespace(api_key, ALCHEMY_API_KEY, exception=BoSettingsError)
        preconditions.check_not_none_or_whitespace(tags_file, TAGS_FILE, exception=BoSettingsError)
        preconditions.check_not_none(tag_match_threshold, TAG_MATCH_THRESHOLD, exception=BoSettingsError)
        preconditions.check_not_none(relevance_threshold, RELEVANCE_THRESHOLD, exception=BoSettingsError)
        preconditions.check_not_none(api_retry_delay_minutes, ALCHEMY_API_RETRY_DELAY_MINUTES,
                                     exception=BoSettingsError)
        preconditions.check_not_none(case_insensitive_tags, CASE_INSENSITIVE_TAGS, exception=BoSettingsError)

        return cls(api_key, tags_file, tag_match_threshold, case_insensitive_tags, relevance_threshold,
                   api_retry_delay_minutes)

    def read_tags_from_file(self, tags_file):
        tags = set()
        with open(tags_file, 'r') as f:
            for line in f:
                tag = line.strip().lower() if self.case_insensitive_tags else line.strip()
                if tag != '':
                    tags.add(tag)
        return tags

    def error_safe_api_executor(self, api_func):
        result = api_func()

        while result['status'].lower() == 'error' and result['statusInfo'] == 'daily-transaction-limit-exceeded':
            wait_until = datetime.datetime.now() + datetime.timedelta(minutes=self.api_retry_delay_minutes)

            logging.info(
                    "Today's Alchemy API transaction limit reached. Suspending until {0}.".format(
                            wait_until))
            pause.until(wait_until)
            result = api_func()

        if result['status'].lower() == 'error':
            raise DropItem("Alchemy returned unknown Error : '{0}'".format(result['statusInfo']))

        return result


class NLPPerformingStage(AlchemyNLPStage):
    def process_item(self, bo_pipeline_item, spider):
        entities_nlp_result, keywords_nlp_result, concepts_nlp_result = self.do_nlp(bo_pipeline_item)
        bo_pipeline_item.update(entities_nlp_result=entities_nlp_result,
                                concepts_nlp_result=concepts_nlp_result,
                                keywords_nlp_result=keywords_nlp_result)
        return bo_pipeline_item

    def do_nlp(self, bo_pipeline_item):
        entities_nlp_result = self.error_safe_api_executor(
                lambda: self.alchemy_api.entities(URL_FLAVOUR, bo_pipeline_item.get_url(), options={'sentiment': 1}))
        keywords_nlp_result = self.error_safe_api_executor(
                lambda: self.alchemy_api.keywords(URL_FLAVOUR, bo_pipeline_item.get_url(), options={'sentiment': 1}))
        concepts_nlp_result = self.error_safe_api_executor(
                lambda: self.alchemy_api.concepts(URL_FLAVOUR, bo_pipeline_item.get_url()))
        return entities_nlp_result, keywords_nlp_result, concepts_nlp_result


class TagAnalysisStage(AlchemyNLPStage):
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
            {self.extract_text(item): {
                'count': int(item['count']) if 'count' in item else None,
                'relevance': float(item['relevance']),
                'sentiment': None if 'sentiment' not in item else (
                    0 if item['sentiment']['type'] == 'neutral' else float(item['sentiment']['score'])),
                'mixed': None if 'sentiment' not in item else (
                    False if 'mixed' not in item['sentiment'] else float(item['sentiment']['mixed']) == 1)
            }
             for item in api_response[api_name] if
             float(item['relevance']) >= self.relevance_threshold}

    def extract_text(self, item):
        # Remove any periods in the tag name (e['text']), because MongoDB doesn't allow keys to have periods in them
        # This doesn't really affect anything, because a random period doesn't mean anything
        return item['text'].replace('.', '').lower() if self.case_insensitive_tags else item[
            'text'].replace('.', '')


class RelevanceFiltrationStage(AlchemyNLPStage):
    def process_item(self, bo_pipeline_item, spider):
        tags = bo_pipeline_item['tags']
        match_count = conditional_count(tags, lambda tag: tags[tag][TAG_MATCHED_KEY] != 'no')

        if match_count < self.tag_match_threshold:
            raise DropItem("Dropping page '{0}' because tag match count = {1} < threshold = {2}"
                           .format(bo_pipeline_item.get_url(), match_count, self.tag_match_threshold))

        return bo_pipeline_item


class PageOverallAnalysisStage(AlchemyNLPStage):
    def process_item(self, bo_pipeline_item, spider):
        sentiment_nlp_result = self.error_safe_api_executor(
                lambda: self.alchemy_api.sentiment(URL_FLAVOUR, bo_pipeline_item.get_url()))
        category_nlp_result = self.error_safe_api_executor(
                lambda: self.alchemy_api.category(URL_FLAVOUR, bo_pipeline_item.get_url()))
        bo_pipeline_item.update(sentiment_nlp_result=sentiment_nlp_result,
                                category_nlp_result=category_nlp_result)
        return bo_pipeline_item
