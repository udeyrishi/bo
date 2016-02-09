from scrapy.exceptions import CloseSpider


class ArgumentNoneError(CloseSpider):
    """
    Exception raised when an argument is None.
    """
    def __init__(self, reason='argument-none'):
        super(BoSettingsError, self).__init__(reason)


class BoSettingsError(CloseSpider):
    """
    A CloseSpider exception raised when the Bo settings are improperly configured.
    """
    def __init__(self, reason='bad-settings'):
        super(BoSettingsError, self).__init__(reason)
