import bo.libs.alchemyapi_python.alchemyapi


class AlchemyNLPPipeline(object):
    def __init__(self, alchemy_api_key):
        self.alchemy_api_key = alchemy_api_key

    @classmethod
    def from_crawler(cls, crawler):
        return cls(alchemy_api_key=crawler.settings.get('ALCHEMY_API_KEY'))
