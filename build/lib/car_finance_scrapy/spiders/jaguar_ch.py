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
################  PCP AND HP ##############

class JaguarSpider(BaseSpider):
    name = "jaguar.co.uk_ch"
    allowed_domains = []
    holder = list()
    start_url = 'https://financecalculator.jaguar.com/api/qq/en/gb/nameplates?financeType=PCH'
    base_url = 'https://www.landrover.co.uk'

    def __init__(self):
        super(JaguarSpider, self).__init__()
        self.i = 0
        # self.XPATH_CATEGORY_LEVEL_1 = '//div[@class="el gridEl"]'


    def start_requests(self):
        """ Start request
        """
        yield Request(self.start_url, callback=self.parse_car_ch, headers=self.headers)
        ##################### BUSINESS Contract HIRE ###################
                        #####  Start here ######
        ###############################################################


    def parse_car_ch(self, response):

        json_data = json.loads(response.body)
        data_loop = json_data['nameplates']
        for car_data in data_loop:
            model = car_data['title']
            link_code = car_data['href']
            href = 'https://financecalculator.jaguar.com/api/qq/en/gb/'+link_code
            yield Request(href, callback=self.parse_car_full_model, headers=self.headers, meta={"model":model})

    def parse_car_full_model(self, response):

        model = response.meta['model']

        json_data = json.loads(response.body)
        # print("json_data:", json_data)
        # print("url:", response.url)
        # input("stop1")
        vehicleData = json_data['availableConfigs']
        nameplateTitle = vehicleData['nameplateTitle']
        collections = vehicleData['collections']
        engines_desc = vehicleData['engines']
        for eng_col in engines_desc:
            for link in collections:
                collections_id = link['id']
                model_spec = link['description']
                car_models = model +" "+ model_spec
                basePrice = link['basePrice']
                carImgurl = link['thumbnail']

                eng_collections = eng_col['collections']
                if collections_id in eng_collections:
                    url_ModelSpec = link['href']
                    weburl = 'https://www.jaguar.co.uk/offers-and-finance/finance-calculator.html#/quote/'+url_ModelSpec
                    full_engine = eng_col['description']
                    car_model = car_models +" ("+ full_engine+")"
                    vehicleTirm = model_spec +'%7C'+ full_engine
                    print("weburl:", weburl)
                    print("resp:", response.url)
                    print("model_spec:", model_spec)
                    print("model:", model)
                    print("car_model:", car_model)
                    print("full_engine:", full_engine)
                    print("collections_id:", collections_id)
                    print("vehicleTirm:", vehicleTirm)
                    # input("stop")
                    QuoteLink = 'https://financecalculator.jaguar.com/api/qq/en/gb/'+url_ModelSpec+'/quote?advanceRental=1&duration=48&mileage=10000&additionalServicesList=0&appName=QQ&basePrice='+str(basePrice)+'&co2Amount=0&financeType=PERSONAL&maintenance=Jaguar%20Maintained&nameplate=f-type&product=PCH&productType=PCH&tradeInOwed=0&tradeInValue=0&vehicleTrim='+vehicleTirm
                    
                    # print("QuoteLink:", QuoteLink)
                    # input("stop")
                    # bootstrap_link = 'https://financecalculator.jaguar.com/api/qq/en/gb/'+url_ModelSpec+'/bootstrap?appName=QQ&product=PCH&financeType=PERSONAL'
                    yield Request(QuoteLink, callback=self.parse_all_ch_data, headers=self.headers, meta={"car_model":car_model, "carImgurl":carImgurl, "weburl":weburl, "url_ModelSpec":url_ModelSpec})

    # def parse_business_car_deposit(self, response):
    #     """FOR parse_car_deposit
    #     """
    #     WebpageURL = response.meta['weburl']
    #     car_model = response.meta['car_model']
    #     carImgurl = response.meta['carImgurl']
    #     url_ModelSpec = response.meta['url_ModelSpec']
    #     json_data = json.loads(response.body)
    #     finance = json_data['finance']
    #     sliders = finance['sliders'][0]
    #     paymentPlan = sliders['value'] ### 3, 6 ,9
    #     term = finance['sliders'][1]
    #     type_finacne = term['value'] ### 36, 48
    #     href = 'https://financecalculator.jaguar.com/api/qq/en/gb/'+url_ModelSpec+'/sliders?appName=QQ&product=PCP&paymentPlan=9&duration=48&mileage=10000&productType=PCH&financeType=PERSONAL&co2Amount=0'
    #     yield Request(href, callback=self.parse_all_ch_data, headers=self.headers, meta={"car_model":car_model, "carImgurl":carImgurl, "WebpageURL":WebpageURL})

    def parse_all_ch_data(self, response):
        """FOR full data
        """

        WebpageURL = response.meta['weburl']
        car_model = response.meta['car_model']
        carImgurl = response.meta['carImgurl']
        json_data = json.loads(response.body)
        # print("json_data:", json_data)
        # print("url:", response.url)
        # input("stop1")
        quoteItems = json_data['quoteItems']
        ### Making Dictionary of One by one item coming in loop
        data = dict()
        for vehicle_data in quoteItems:
            key = vehicle_data['key']
            value = vehicle_data['value']
            data.update({key:value})

        # print("response:", response.url)
        # # print("data:", data)
        # print("key:", key)
        # # print("TypeofFinance:", json_data)
        # input("stop")

        initialPayment = data['InitialRental']
        annualMileage = data['MileagePerAnnum']
        MonthlyPayment = data['monthlyPayment']
        term = data['ContractLength']
        excess_milage_charge = data['ExcessMileageMinimalDecimals']

        # # print("slice:", slice)
        # # print("resp:", response.url)
        # # print("initialPayment:", initialPayment)
        # # print("annualMileage:", annualMileage)
        # # print("MonthlyPayment:", MonthlyPayment)
        # # print("term:", term)
        # # print("car_model:", car_model)
        # input("stop")

        car_make = 'Jaguar'
        item = CarItem()
        item['CarMake'] = car_make
        if "‑" in car_model:
            car_model = car_model.replace("‑", "-")
        car_model = car_model.split()
        CarModel = " ".join(sorted(set(car_model), key=car_model.index))
        if "NEW JAGUAR " in CarModel:
            item['CarModel'] = CarModel.split("NEW JAGUAR ")[1]
        elif "JAGUAR " in CarModel:
            item['CarModel'] = CarModel.split("JAGUAR ")[1]
        else:
            item['CarModel'] = CarModel
        item['TypeofFinance'] = self.get_type_of_finance('PCH')
        item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
        item['CustomerDeposit'] = self.make_two_digit_no(initialPayment)
        item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = 'N/A'
        item['AmountofCredit'] = 'N/A'
        item['DurationofAgreement']   = self.remove_percentage_sign(term)
        item['OptionalPurchase_FinalPayment']   = 'N/A'
        item['TotalAmountPayable'] = 'N/A'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = 'N/A'
        item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        item['ExcessMilageCharge'] = self.remove_percentage_sign(excess_milage_charge)
        item['AverageMilesPerYear'] = self.remove_percentage_sign(annualMileage)
        item['RetailCashPrice'] = 'N/A'
        item['OfferExpiryDate'] = 'N/A'
        item['WebpageURL'] = WebpageURL
        item['DebugMode'] = self.Debug_Mode
        item['CarimageURL'] = carImgurl
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        if item['MonthlyPayment'] != '' and item['CarModel'] != '':
            yield item
