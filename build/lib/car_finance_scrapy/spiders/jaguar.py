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
    name = "jaguar.co.uk"
    allowed_domains = []
    holder = list()
    start_url = 'https://financecalculator.jaguar.com//api/qq/en/gb/nameplates?financeType=PERSONAL'
    base_url = 'https://www.jaguar.co.uk/'

    def __init__(self):
        super(JaguarSpider, self).__init__()
        self.i = 0
        # self.XPATH_CATEGORY_LEVEL_1 = '//div[@class="el gridEl"]'


    # def start_requests(self):
    #     for url in self.start_url:
    #
    #         if "financeType=PERSONAL" in url:
    #             yield Request(url, callback=self.parse_category_pcp, headers=self.headers)
    #         else:
    #             yield Request(url, callback=self.parse_car_ch, headers=self.headers)

    def start_requests(self):
        """ Start request
        """
        yield Request(self.start_url, callback=self.parse_category_pcp, headers=self.headers)

    def parse_category_pcp(self, response):

        json_data = json.loads(response.body)
        data_loop = json_data['nameplates']
        for car_data in data_loop:
            model = car_data['title']
            link_code = car_data['href']
            href = 'https://financecalculator.jaguar.com//api/qq/en/gb/'+link_code

            yield Request(href, callback=self.parse_full_model_pcp, headers=self.headers, meta={"model":model})

    def parse_full_model_pcp(self, response):

        model = response.meta['model']

        json_data = json.loads(response.body)

        vehicleData = json_data['availableConfigs']
        collections = vehicleData['collections']
        engines_desc = vehicleData['engines']
        for eng_col in engines_desc:
            for link in collections:
                collections_id = link['id']
                model_spec = link['description']
                car_models = model +" "+ model_spec
                # basePrice_otr = link['basePrice']
                carImgurl = link['thumbnail']

                eng_collections = eng_col['collections']
                if collections_id in eng_collections:
                    url_ModelSpec = link['href']
                    weburl = 'https://www.jaguar.co.uk/offers-and-finance/finance-calculator.html#/quote/'+url_ModelSpec
                    full_engine = eng_col['description']
                    car_model = car_models +" ("+ full_engine+")"

                    bootstrap_link = 'https://financecalculator.jaguar.com//api/qq/en/gb/'+url_ModelSpec+'/bootstrap?appName=QQ&product=PCP&financeType=PERSONAL'
                    yield Request(bootstrap_link, callback=self.parse_car_deposit_pcp, headers=self.headers, meta={"car_model":car_model, "carImgurl":carImgurl, "weburl":weburl, "url_ModelSpec":url_ModelSpec})

    def parse_car_deposit_pcp(self, response):
        """FOR parse_car_deposit
        """


        WebpageURL = response.meta['weburl']
        car_model = response.meta['car_model']
        carImgurl = response.meta['carImgurl']
        url_ModelSpec = response.meta['url_ModelSpec']
        json_data = json.loads(response.body)
        product = json_data['products']
        finance = json_data['finance']
        sliders = finance['sliders'][0]
        deposit = sliders['value']
        for type in product:
            TypeofFinance = type['type']
            href = 'https://financecalculator.jaguar.com//api/qq/en/gb/'+url_ModelSpec+'/sliders?appName=QQ&product='+TypeofFinance+'&deposit='+str(deposit)+'&duration=48&mileage=10000&productType=PCP&financeType=PERSONAL'

            yield Request(href, callback=self.parse_car_data_pcp, headers=self.headers, meta={"car_model":car_model, "carImgurl":carImgurl, "WebpageURL":WebpageURL,"deposit":deposit})

    def parse_car_data_pcp(self, response):
        """FOR full data
        """
        # on_the_road_price = str()
        # customerDeposit = str()
        # AmountofCredit = str()
        # MonthlyPayment = str()
        # OptionalPurchase_FinalPayment = str()
        # TotalAmountPayable = str()
        # duration_of_agreement = str()
        # representative_apr = str()
        # PurchaseActivationFee = str()
        # rate_of_interest = str()
        excess_milage_charge = str()
        averageMilesPerYear = str()
        RetailerDepositContribution = str()

        WebpageURL = response.meta['WebpageURL']
        car_model = response.meta['car_model']
        carImgurl = response.meta['carImgurl']

        # customerDeposit = response.meta['deposit'] ### Deposit Previous

        json_data = json.loads(response.body)
        TypeofFinance = json_data['id'] ### type of finance
        # print("json_data:", json_data)
        # input("stop")
        quoteItems = json_data['quoteItems']
        ### Making Dictionary of One by one item coming in loop
        data = dict()
        for vehicle_data in quoteItems:
            key = vehicle_data['key']
            value = vehicle_data['value']
            data.update({key:value})

        # print("response:", response.url)
        # # print("data:", data)
        # print("data:", data)
        # # print("TypeofFinance:", json_data)
        # input("stop")

        on_the_road_price = data['VehiclePriceIncludingDiscountsExcludingOlev']
        AmountofCredit = data['AmountOfCredit']
        MonthlyPayment = data['RegularPaymentWithoutOnePayment']
        OptionalPurchase_FinalPayment = data['finalPayment']
        TotalAmountPayable = data['totalAmount']
        duration_of_agreement = data['duration']
        customerDeposit = data['deposit']
        representative_apr = data['apr']
        rate_of_interest = data['FixedRateOfInterest']
        if "purchaseFee" in data:
            PurchaseActivationFee = data['purchaseFee']
        else:
            PurchaseActivationFee = 'N/A'
        if "MileagePerAnnum" in data:
            averageMilesPerYear = data['MileagePerAnnum']
        if "Finance Deposit Allowance" in data:
            RetailerDepositContribution = data['Finance Deposit Allowance']
        if "ExcessMileageCharge" in data:
            excess_milage_charge = data['ExcessMileageCharge']

        # # print("slice:", slice)
        # # print("resp:", response.url)
        # # print("on_the_road_prices:", on_the_road_price)
        # # print("customerDeposit:", customerDeposit)
        # # print("AmountofCredit:", AmountofCredit)
        # # print("MonthlyPayment:", MonthlyPayment)
        # # print("TotalAmountPayable:", TotalAmountPayable)
        # # print("car_model:", car_model)

    # print("car_model:", car_model)
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
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
        # if item['MonthlyPayment']:
        #     item['MonthlyPayment'] = float(item['MonthlyPayment'])
        item['CustomerDeposit'] = self.make_two_digit_no(customerDeposit)
        if RetailerDepositContribution:
            item['RetailerDepositContribution'] = self.make_two_digit_no(str(RetailerDepositContribution))
        else:
            item['RetailerDepositContribution'] = 'N/A'

        item['OnTheRoadPrice'] = self.remove_percentage_sign(on_the_road_price)
        if item['OnTheRoadPrice']:
            item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
        item['AmountofCredit'] = self.remove_gbp(AmountofCredit.replace(",", ""))
        item['DurationofAgreement']   = self.remove_percentage_sign(duration_of_agreement)
        item['OptionalPurchase_FinalPayment']   = self.remove_gbp(OptionalPurchase_FinalPayment.replace(",", ""))
        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
        item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(PurchaseActivationFee)
        item['RepresentativeAPR'] = self.remove_percentage_sign(representative_apr)
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(rate_of_interest)
        if excess_milage_charge:
            item['ExcessMilageCharge'] = self.remove_percentage_sign(excess_milage_charge)
        else:
            item['ExcessMilageCharge'] = 'N/A'
        if averageMilesPerYear:
            item['AverageMilesPerYear'] = self.remove_percentage_sign(averageMilesPerYear)
        else:
            item['AverageMilesPerYear'] = 'N/A'
        item['RetailCashPrice'] = self.remove_percentage_sign(on_the_road_price)
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
