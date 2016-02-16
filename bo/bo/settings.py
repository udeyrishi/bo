#################### BO CONFIGURATION #########################
START_URLS_FILE = './urls.csv'
TAGS_FILE = './keywords.txt'
# WARNING: Don't leave the API key in the settings when committing!
ALCHEMY_API_KEY = 'xxx'
TAG_MATCH_THRESHOLD = 5
CASE_INSENSITIVE_TAGS = True
RELEVANCE_THRESHOLD = 0.5
MONGO_DATABASE = 'bo_db'
MONGO_URI = 'mongodb://localhost:27017/'
MONGO_COLLECTION_NAME = 'bo_items'
OUTPUT_FILE = 'output.debug.json'
ALCHEMY_API_RETRY_DELAY_MINUTES = 60
###############################################################

BOT_NAME = 'bo'
SPIDER_MODULES = ['bo.spiders']
NEWSPIDER_MODULE = 'bo.spiders'
ITEM_PIPELINES = {
    'bo.pipelines.alchemy_nlp_pipeline.NLPPerformingStage': 0,
    'bo.pipelines.alchemy_nlp_pipeline.TagAnalysisStage': 1,
    'bo.pipelines.alchemy_nlp_pipeline.RelevanceFiltrationStage': 2,
    'bo.pipelines.alchemy_nlp_pipeline.PageOverallAnalysisStage': 3,
    'bo.pipelines.storage_pipeline.PackagingPipeline': 4,
    # 'bo.pipelines.storage_pipeline.JsonFileWriterStage': 4.5,
    'bo.pipelines.storage_pipeline.MongoStorageStage': 5
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'bo (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'bo.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'bo.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'bo.pipelines.SomePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
