# -*- coding: utf-8 -*-
from http.client import responses
# from matplotlib import image
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


class ToyotaSpider(BaseSpider):
    name = "toyota.offers.co.uk"
    allowed_domains = []
    holder = list()
    start_url = 'https://www.toyota.co.uk/current-offers'
    base_url = 'https://www.toyota.co.uk'
    handle_httpstatus_list = [400,403,404,302]
    def __init__(self):
        super(ToyotaSpider, self).__init__()
        self.i = 0
        self.XPATH_CATEGORY_LEVEL_1 = '//div[@class="filterable-wrapper"]//div[@class="col-xs-12 col-sm-6 filterable responsive-item"]//ul[@class="list-group promo-desc-list col-xs-12"]/li[1]/a/@href'

    def start_requests(self):
        """ Start request for Cars
        """
        yield Request(self.start_url, callback=self.parse_item_list, headers=self.headers_toyota, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com"})
        # yield Request(self.start_url, callback=self.parse_item_list, headers=self.headers_toyota)

    def parse_item_list(self, response):
        """ Function for parse item list
        """
        #URLS = [response.urljoin(link) for link in ]
        URLS = []
        for i in response.xpath('//a[span[contains(text(),"Discover")]]/@href').extract():
            if'/new-cars/' in i:
                URLS.append(response.urljoin(i))
        images = [self.base_url+link for link in response.xpath('//div[@class="card-img"]//img/@src').extract()]
        for num,car_url in enumerate(URLS):
            if '/new-cars/' in car_url:
                image = images[num] 
                yield Request(car_url, callback=self.parse_item_m, headers=self.headers_toyota, meta={"image":image, 'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com"})
                # yield Request(car_url, callback=self.parse_item_m, headers=self.headers_toyota, meta={"image":image})
                #break
   
    def parse_item_m(self,response):
        car_image = response.meta['image']
        if '-retail-offer' in response.url:
            carsdata = response.xpath('//script[contains(text(),"retailoffer")]/text()').get()
            if carsdata != None:
                carsdata = carsdata.replace('window["retailoffer"] = ','').replace(';','')
                main_data = json.loads(carsdata)
                link = self.base_url+main_data.get('navigation',{}).get('Business Contract Hire','N/A')
                if link =='N/A':
                    return
                yield Request(link,callback=self.parse_item_m,meta={'image':car_image}, headers=self.headers_toyota)
                return
        try:
            main_data = json.loads(response.xpath('//script[contains(text(),"bchoffer")]/text()').get().replace('window["bchoffer"] = ','').replace(';',''))
        except:
            return
        
        
        na='N/A'
        onRoadPrice = na
        monthly_installment = self.remove_gbp(main_data.get('promotion',{}).get('monthly',na))
        total_payable_amount = na
        Rate_of_interest = na
        APR = na
        Optional_final_payment = na
        
        deposit = self.remove_gbp( main_data.get('promotion',{}).get('rental',na))
        contract_duration = main_data.get('termsAndConditions',{}).get('term2',na).split('month')[0].split()[-1]
        try:
            CarModels = main_data.get('termsAndConditions',{}).get('term1',na).split("shown is MY22 ")[1].split("£")[0]
            # print("Models:", Models)
            # input("stop")
        except:
            CarModels = main_data.get('termsAndConditions',{}).get('term1',na).split("shown is MY21 ")[1].split("£")[0]
            # print("Models:", Models)
            # input("stop 2")

        # car_model = main_data['config'].get('modelID','N/A')
        mileage = main_data.get('finance',{}).get('mileage','N/A')
        Expiry = main_data.get('promotion',{}).get('notice','N/A').split('until')[-1]
    

        car_make = 'Toyota'
        item = CarItem()
        item['CarMake'] = car_make
        item['CarModel'] = CarModels
        item['TypeofFinance'] = self.get_type_of_finance('BCH')
        item['MonthlyPayment'] = monthly_installment
        item['CustomerDeposit'] = deposit
        item['RetailerDepositContribution']= 'N/A'
        item['OnTheRoadPrice'] = onRoadPrice
        item['AmountofCredit'] = na
        item['DurationofAgreement'] = contract_duration
        item['OptionalPurchase_FinalPayment'] = Optional_final_payment
        item['TotalAmountPayable'] = total_payable_amount
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = APR
        item['FixedInterestRate_RateofinterestPA'] = Rate_of_interest
        item['ExcessMilageCharge'] = 'N/A'
        item['AverageMilesPerYear'] = mileage
        item['OfferExpiryDate'] = Expiry
        item['RetailCashPrice'] = onRoadPrice
        item['WebpageURL'] = response.url
        item['CarimageURL'] = car_image
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        item['DebugMode'] = self.Debug_Mode
        yield item


  