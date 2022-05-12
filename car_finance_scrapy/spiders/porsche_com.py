# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
import urllib
import json
from datetime import datetime, timedelta
from time import gmtime, strftime
from dateutil.relativedelta import relativedelta
import re
from urllib.parse import urljoin
from html.parser import HTMLParser
from requests import Session

class PorscheSpider(BaseSpider):
    name = "porsche.com"

    allowed_domains = ['www.porsche.com']

    start_url = 'https://www.porsche.com/uk/models'
    def __init__(self):
        super(PorscheSpider, self).__init__()

    def start_requests(self):
        yield Request(self.start_url, callback=self.parse_model_url, headers=self.headers)

    models = {}
    def parse_model_url(self, response):
        for a in response.xpath('//div[@class="m-14-model-tile-link-overview"]'):
            model =  self.getText(a, './*/img/@alt')
            modelUrl = response.urljoin(self.getText(a, './@href')) + 'finance/'
            self.models[model] = modelUrl
            modelImageUrl = self.getText(a, './*/img/@src')
            yield Request(modelUrl, callback=self.parse_model, headers=self.headers,\
                          meta={'model': model,'modelImageUrl': modelImageUrl})

    def parse_model(self, response):

        body = response.body.decode('utf-8')
        # Parse data here
        item = CarItem()
        item['CarMake'] = 'Porsche'
        item['CarModel'] = self.remove_special_char_on_excel(response.meta.get('model'))
        item['TypeofFinance'] = self.get_type_of_finance('PCP')
        item['MonthlyPayment'] = self.remove_gbp(self.getText(response, '//*[contains(text()," monthly payments of")]/../*[2]/text()'))
        item['CustomerDeposit'] = self.remove_gbp(self.getText(response, '//*[contains(text(),"Customer deposit")]/../*[2]/text()'))
        item['RetailerDepositContribution'] = self.remove_gbp(self.getText(response, '//*[contains(text(),"Deposit Contribution")]/../*[2]/text()'))
        item['OnTheRoadPrice'] = self.remove_gbp(self.getText(response, '//*[contains(text(),"Recommended on-the-road price")]/../*[2]/text()'))
        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(self.getText(response, '//*[contains(text(),"Optional final payment")]/../*[2]/text()'))
        item['AmountofCredit'] = self.remove_gbp(self.getText(response, '//*[contains(text(),"Total amount of credit")]/../*[2]/text()'))
        item['DurationofAgreement'] = self.getText(response, '//*[contains(text(),"Duration")]/../*[2]/text()').split("months")[0]
        item['TotalAmountPayable'] = self.remove_gbp(self.getText(response, '//*[contains(text(),"Total amount payable")]/../*[2]/text()'))
        item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(self.getText(response, '//*[contains(text(),"Option to purchase fee")]/../*[2]/text()'))
        item['RepresentativeAPR'] = self.getText(response, '//*[contains(text(),"Representative APR")]/../*[2]/text()').split("APR")[0]
        item['FixedInterestRate_RateofinterestPA'] = self.getText(response, '//*[contains(text(),"Rate of Interest")]/../*[2]/text()').split("fixed")[0]
        item['ExcessMilageCharge'] = self.getText(response, '//*[contains(text(),"Excess mileage")]/../*[2]/text()').split("p")[0]
        item['AverageMilesPerYear'] = self.reText(body, r'(\d+,\d+ mile) per annum agreement').split("mile")[0]
        item['RetailCashPrice'] = self.remove_gbp(self.getText(response, '//*[contains(text(),"Recommended on-the-road price")]/../*[2]/text()'))
        item['CarimageURL'] = response.meta.get('modelImageUrl')
        item['OfferExpiryDate'] = 'N/A'
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        if item['MonthlyPayment'] != '':
            yield item
