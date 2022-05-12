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
################  PCP AND Contract hire ##############

class LandroverSpider(BaseSpider):
    name = "landrover.co.uk"
    allowed_domains = []
    holder = list()
    start_url = ['https://financecalculator.landrover.com//api/qq/en/gb/nameplates?financeType=PERSONAL', 'https://financecalculator.landrover.com//api/qq/en/gb/nameplates?financeType=BUSINESS']
    base_url = 'https://www.landrover.co.uk'

    def __init__(self):
        super(LandroverSpider, self).__init__()
        self.i = 0
        self.XPATH_CATEGORY_LEVEL_1 = '//div[@class="el gridEl"]'


    def start_requests(self):
        """ Start request
        """
        for url in self.start_url:
            if "PERSONAL" in url:
                yield Request(url, callback=self.parse_category, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_contract_hire_url, headers=self.headers)

    def parse_category(self, response):
        json_data = json.loads(response.body)
        data_loop = json_data['nameplates']
        for car_data in data_loop:
            model = car_data['title']
            link_code = car_data['href']
            href = 'https://financecalculator.landrover.com//api/qq/en/gb/'+link_code

            yield Request(href, callback=self.parse_full_model, headers=self.headers, meta={"model":model})

    def parse_contract_hire_url(self, response):

        json_data = json.loads(response.body)
        data_loop = json_data['nameplates']
        for car_data in data_loop:
            model = car_data['title']
            link_code = car_data['href']
            href = 'https://financecalculator.landrover.com//api/qq/en/gb/'+link_code

            yield Request(href, callback=self.parse_ch_full_offer, headers=self.headers, meta={"model":model})

    def parse_full_model(self, response):

        model = response.meta['model']

        json_data = json.loads(response.body)
        # availableConfigs
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
                    weburl = 'https://www.landrover.co.uk/offers-and-finance/finance-calculator.html#/quote/'+url_ModelSpec
                    full_engine = eng_col['description']
                    car_model = car_models +" ("+ full_engine+")"

                    bootstrap_link = 'https://financecalculator.landrover.com//api/qq/en/gb/'+url_ModelSpec+'/bootstrap?appName=QQ&product=PCP&financeType=PERSONAL'
                    yield Request(bootstrap_link, callback=self.parse_car_deposit, headers=self.headers, meta={"car_model":car_model, "carImgurl":carImgurl, "weburl":weburl, "url_ModelSpec":url_ModelSpec})

    def parse_car_deposit(self, response):
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
            href = 'https://financecalculator.landrover.com//api/qq/en/gb/'+url_ModelSpec+'/sliders?appName=QQ&product='+TypeofFinance+'&deposit='+str(deposit)+'&duration=48&mileage=10000&productType=PCP&financeType=PERSONAL'

            yield Request(href, callback=self.parse_car_data, headers=self.headers, meta={"car_model":car_model, "carImgurl":carImgurl, "WebpageURL":WebpageURL,"deposit":deposit})

    def parse_car_data(self, response):
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
        PurchaseActivationFee = str()
        WebpageURL = response.meta['WebpageURL']
        car_model = response.meta['car_model']
        carImgurl = response.meta['carImgurl']

        customerDeposit = response.meta['deposit']
        json_data = json.loads(response.body)
        TypeofFinance = json_data['id'] ### type of finance
        quoteItems = json_data['quoteItems']
        ### Making Dictionary of One by one item coming in loop
        data = dict()
        for vehicle_data in quoteItems:
            key = vehicle_data['key']
            value = vehicle_data['value']
            data.update({key:value})

        # print("response:", response.url)
        # print("data:", data)
        # print("key:", key)
        # input("stop")

        on_the_road_price = data['VehiclePriceIncludingDiscountsExcludingOlev']
        AmountofCredit = data['AmountOfCredit']
        MonthlyPayment = data['RegularPaymentWithoutOnePayment']
        OptionalPurchase_FinalPayment = data['finalPayment']
        TotalAmountPayable = data['totalAmount']
        duration_of_agreement = data['duration']
        representative_apr = data['apr']
        rate_of_interest = data['FixedRateOfInterest']
        if "purchaseFee" in data:
            PurchaseActivationFee = data['purchaseFee']
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

        car_make = 'Range Rover'
        item = CarItem()
        item['CarMake'] = car_make
        if "‑" in car_model:
            car_model = car_model.replace("‑", "-")
        car_model = car_model.split()
        item['CarModel'] = " ".join(sorted(set(car_model), key=car_model.index))
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
        # if item['MonthlyPayment']:
        #     item['MonthlyPayment'] = float(item['MonthlyPayment'])
        item['CustomerDeposit'] = self.make_two_digit_no(str(customerDeposit))
        if RetailerDepositContribution:
            item['RetailerDepositContribution'] = self.remove_percentage_sign(RetailerDepositContribution)
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
        item['ExcessMilageCharge'] = self.remove_percentage_sign(excess_milage_charge)
        item['AverageMilesPerYear'] = self.remove_percentage_sign(averageMilesPerYear)
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

    def parse_ch_full_offer(self, response):

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
                carImgurl = link['thumbnail']

                eng_collections = eng_col['collections']
                if collections_id in eng_collections:
                    url_ModelSpec = link['href']
                    weburl = 'https://www.landrover.co.uk/offers-and-finance/finance-calculator.html#/quote/'+url_ModelSpec
                    full_engine = eng_col['description']
                    car_model = car_models +" ("+ full_engine+")"
                    # print("weburl:", weburl)
                    # print("resp:", response.url)
                    # print("car_model:", car_model)
                    # print("full_engine:", full_engine)
                    # print("collections_id:", collections_id)
                    # print("eng_collection:", eng_collections)
                    # input("stop")
                    bootstrap_link = 'https://financecalculator.landrover.com//api/qq/en/gb/'+url_ModelSpec+'/bootstrap?appName=QQ&product=PCP&financeType=BUSINESS'
                    yield Request(bootstrap_link, callback=self.parse_ch_car_deposit, headers=self.headers, meta={"car_model":car_model, "carImgurl":carImgurl, "weburl":weburl, "url_ModelSpec":url_ModelSpec})

    def parse_ch_car_deposit(self, response):
        """FOR parse_car_deposit
        """
        WebpageURL = response.meta['weburl']
        car_model = response.meta['car_model']
        carImgurl = response.meta['carImgurl']
        url_ModelSpec = response.meta['url_ModelSpec']
        json_data = json.loads(response.body)
        finance = json_data['finance']
        sliders = finance['sliders'][0]
        paymentPlan = sliders['value'] ### 3, 6 ,9
        term = finance['sliders'][1]
        type_finacne = term['value'] ### 36, 48
        href = 'https://financecalculator.landrover.com//api/qq/en/gb/'+url_ModelSpec+'/sliders?appName=QQ&product=PCP&paymentPlan=9&duration=48&mileage=10000&productType=PCP&financeType=BUSINESS&co2Amount=0'
        yield Request(href, callback=self.parse_ch_car_data, headers=self.headers, meta={"car_model":car_model, "carImgurl":carImgurl, "WebpageURL":WebpageURL})

    def parse_ch_car_data(self, response):
        """FOR full data
        """

        WebpageURL = response.meta['WebpageURL']
        car_model = response.meta['car_model']
        carImgurl = response.meta['carImgurl']
        json_data = json.loads(response.body)

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

        initialPayment = data['initialPayment']
        annualMileage = data['annualMileage']
        MonthlyPayment = data['monthlyRental']
        term = data['term']
        excess_milage_charge = data['excessMileage']

        # # print("slice:", slice)
        # # print("resp:", response.url)
        # # print("initialPayment:", initialPayment)
        # # print("annualMileage:", annualMileage)
        # # print("MonthlyPayment:", MonthlyPayment)
        # # print("term:", term)
        # # print("car_model:", car_model)
        # input("stop")

        car_make = 'Range Rover'
        item = CarItem()
        item['CarMake'] = car_make
        if "‑" in car_model:
            car_model = car_model.replace("‑", "-")
        car_model = car_model.split()
        item['CarModel'] = " ".join(sorted(set(car_model), key=car_model.index))
        item['TypeofFinance'] = self.get_type_of_finance('BCH')
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
