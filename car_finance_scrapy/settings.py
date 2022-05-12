# -*- coding: utf-8 -*-

# Scrapy settings for car_finance_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'car_finance_scrapy'

SPIDER_MODULES = ['car_finance_scrapy.spiders']
NEWSPIDER_MODULE = 'car_finance_scrapy.spiders'
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408, 429]
# RETRY_HTTP_CODES = [500, 502, 503, 504, 403, 404, 408, 429]
HTTPERROR_ALLOWED_CODES = [404, 400, 403, 301]

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1
}
# DOWNLOADER_MIDDLEWARES = {
#     # 'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 90,
#     # Fix path to this module
#     'car_finance_scrapy.randomproxy.RandomProxy': 100,
#     # 'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
# }
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'car_finance_scrapy (+http://www.yourdomain.com)'

# USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/95.0.4638.50 Mobile/15E148 Safari/604.1'
# Obey robots.txt rules
# ROBOTSTXT_OBEY = True
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32


FEED_EXPORT_FIELDS = [
    'CarMake',
    'CarModel',
    'TypeofFinance',
    'MonthlyPayment',
    'CustomerDeposit',
    'RetailerDepositContribution',
    'RepresentativeAPR',
    'TotalAmountPayable',
    'OnTheRoadPrice',
    'DurationofAgreement',
    'OptionalPurchase_FinalPayment',
    'AmountofCredit',
    'OptionToPurchase_PurchaseActivationFee',
    'FixedInterestRate_RateofinterestPA',
    'ExcessMilageCharge',
    'AverageMilesPerYear',
    'RetailCashPrice',
    'OfferExpiryDate',
    'DepositPercent',
    'FinalPaymentPercent',
    'WebpageURL',
    'CarimageURL',
]

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'car_finance_scrapy.middlewares.CarFinanceScrapySpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'car_finance_scrapy.middlewares.MyCustomDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'car_finance_scrapy.pipelines.CarFinanceScrapyPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
