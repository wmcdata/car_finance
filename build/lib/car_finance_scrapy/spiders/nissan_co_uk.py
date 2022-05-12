
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
import requests
from urllib.parse import urljoin
from html.parser import HTMLParser
from requests import Session

#####################
#################### ALL PCP AND CH , CARS AND VANS
#####################



class NissanSpider(BaseSpider):
    name = "nissan.co.uk"
    allowed_domains = []
    holder = list()

    # WebStartLINK =  "https://www.nissan.co.uk/offers.html#category=Personal+Finance"

    start_url = ['https://eu.nissan-api.net/v2/offers?category=Personal+Finance&location=&model=&grade=&version=&type=Personal+Contract+Purchase&start=0&size=6&includeResults=true&includeFilteredFacets=true&includePreFilteredFacets=false', 'https://eu.nissan-api.net/v2/offers?category=Business+Finance&location=&model=&grade=&version=&type=Business+Contract+Hire&start=0&size=6&includeResults=true&includeFilteredFacets=true&includePreFilteredFacets=false']

    base_url = 'https://www.nissan.co.uk'

    def __init__(self):
        super(NissanSpider, self).__init__()
        self.i = 0
        self.XPATH_CATEGORY_LEVEL_1 = '//div[@class="toggle-columns parsys"]/div[@class="column columns444 columns section"]//ul[@class="cta-list"]/li[1]/a[contains(text(), "VIEW OFFERS")]/@href'
        self.XPATH_CATEGORY_LEVEL_VANS = '//div[@class="vehicle-link"]//div[@class="starting-price"]//ul[@class="prices"]/li/div[@class="subtext"]/a/@href'


    def start_requests(self):
        """ Start request
        """
        headers = {
            'accept': "*/*",
            'apikey': "8GspOAJAHvLp50h8piCeNGjYfuSZlHqr",
            'clientkey': "h84dIG2S17QNq6j9fgvv6t3KXBQRJJts",
            'origin': "https://www.nissan.co.uk",
            'referer': "https://www.nissan.co.uk/offers.html",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            'cache-control': "no-cache",
            'postman-token': "77117ea0-2f32-a72b-2de7-f3c0904dfc21"
            }

        for url in self.start_url:
            if "Personal+Finance" in url:
                yield Request(url, callback=self.parse_item_list_PCP, headers=headers)
            # else:
            #     yield Request(url, callback=self.parse_car_vans_CH, headers=headers)



    def parse_item_list_PCP(self, response):
        """ Function for parse item list
        """
        # querystring = {"includeResults":"false","includeFilteredFacets":"false","includePreFilteredFacets":"true"}
        ### Here we are taking Respon.url for Link ### Start link
        headers = {
            'Accept': "*/*",
            'apiKey': "8GspOAJAHvLp50h8piCeNGjYfuSZlHqr",
            'clientKey': "h84dIG2S17QNq6j9fgvv6t3KXBQRJJts",
            'Origin': "https://www.nissan.co.uk",
            'Referer': "https://www.nissan.co.uk/offers.html",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            }

        response = requests.request("GET", response.url, headers=headers)

        model_data = response.json()

        facets = model_data['facets']
        preFiltered = facets['filtered']
        models = preFiltered['models']

        for model_number in models:
            model_key = model_number['key']
            ### Here we are taking Below link URL and Using Above Header
            url = 'https://eu.nissan-api.net/v2/offers?category=Personal+Finance&location=&model='+model_key+'&grade=&version=&type=&start=0&size=6&includeResults=true&includeFilteredFacets=true&includePreFilteredFacets=false'
            yield Request(url, callback=self.parse_item, headers=headers)

    def parse_car_vans_CH(self, response):
        """ Function for parse item list
        """
        # print("url", response.url)
        # # print("response", url)
        # input("stop1")

        ### Here we are taking Respon.url for Link ### Start link

        headers = {
            'Accept': "*/*",
            'apiKey': "8GspOAJAHvLp50h8piCeNGjYfuSZlHqr",
            'clientKey': "h84dIG2S17QNq6j9fgvv6t3KXBQRJJts",
            'Origin': "https://www.nissan.co.uk",
            'Referer': "https://www.nissan.co.uk/offers.html",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            }

        response = requests.request("GET", response.url, headers=headers)
        model_data = response.json()
        facets = model_data['facets']

        preFiltered = facets['filtered']
        models = preFiltered['models']
        for model_number in models:
            model_key = model_number['key']
            ### Here we are taking Below link URL and Using Above Header
            url = 'https://eu.nissan-api.net/v2/offers?category=Business+Finance&location=&model='+model_key+'&grade=&version=&type=Business+Contract+Hire&start=0&size=6&includeResults=true&includeFilteredFacets=true&includePreFilteredFacets=false'
            yield Request(url, callback=self.parse_car_vans_item, headers=headers)

    def parse_item(self, response):
        """ Function for parse item
        """
        headers = {
            'Accept': "*/*",
            'apiKey': "8GspOAJAHvLp50h8piCeNGjYfuSZlHqr",
            'clientKey': "h84dIG2S17QNq6j9fgvv6t3KXBQRJJts",
            'Origin': "https://www.nissan.co.uk",
            'Referer': "https://www.nissan.co.uk/offers.html",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            }
        json_data = json.loads(response.body)
        if "offers" in json_data:
            offers = json_data['offers']
            for ID in offers:
                model_id = ID['id']
                url = 'https://eu.nissan-api.net/v2/offers/'+model_id+''
                yield Request(url, callback=self.parse_item_data, headers=headers)

    ######################## CH  VANS AND CARS ###############################
    ######################## CH  VANS AND CARS  ###############################
    def parse_car_vans_item(self, response):
        """ Function for parse item
        """
        headers = {
            'Accept': "*/*",
            'apiKey': "8GspOAJAHvLp50h8piCeNGjYfuSZlHqr",
            'clientKey': "h84dIG2S17QNq6j9fgvv6t3KXBQRJJts",
            'Origin': "https://www.nissan.co.uk",
            'Referer': "https://www.nissan.co.uk/offers.html",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
            }
        json_data = json.loads(response.body)
        if "offers" in json_data:
            offers = json_data['offers']
            for ID in offers:
                model_id = ID['id']
                url = 'https://eu.nissan-api.net/v2/offers/'+model_id+''
                yield Request(url, callback=self.parse_car_vans_data, headers=headers)


    def parse_car_vans_data(self, response):
        """ Function for parse DATA
        """
        json_data = json.loads(response.body)

        carImgurl = json_data['images']['detail']['mediumStdRes']
        TypeofFinance = json_data['offerType']

        ############# url making #############
        carID = json_data['id']
        weburl = 'https://www.nissan.co.uk/offers.html#category=Business+Finance&type=Contract+Hire&type=Finance+Lease&offerId='+carID+''
        ############# url making #############

        model = json_data['model']['name']
        post_modelName = json_data['applicability']
        CarModel = model +" "+ post_modelName
        offer_text =json_data['legals']['main']['details']
        offerExp = offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        OfferExpiryDate = self.dateMatcher(offerExp)[1]

        # print("OfferExpiryDate: ", OfferExpiryDate)
        # input("stop ")
        # if "ordered by" in offer_text:
        #     OfferExpiryDate = offer_text.split("ordered by")[1].split(".")[0]
        # elif "] by " in offer_text:
        #     OfferExpiryDate = offer_text.split("] by ")[1].split(".")[0]

        if "Excess Mileage charged" in offer_text:
            ExcessMilageCharge = offer_text.split("Excess Mileage charged at ")[1].split("p")[0]
        else:
            ExcessMilageCharge = 'N/A'
        quoteItems = json_data['table']['data']

        data = dict()
        for vehicle_data in quoteItems:
            key = vehicle_data['label']
            value = vehicle_data['value']
            data.update({key:value})

        # print("weburl: ",weburl)
        # print("data: ", data)
        # input("stop")
        if "Monthly Payment" in data:
            MonthlyPayment = data['Monthly Payment']
        elif "Monthly Payment (excl. VAT)" in data:
            MonthlyPayment = data['Monthly Payment (excl. VAT)']
        else:
            MonthlyPayment = 'N/A'

        if "On the Road Cash Price" in data:
            on_the_road_price = data['On the Road Cash Price']
        elif "CV On the Road Price (excl. VAT)" in data:
            on_the_road_price = data['CV On the Road Price (excl. VAT)']
        else:
            on_the_road_price = 'N/A'

        if "Initial Rental" in data:
            CustomerDeposit = data['Initial Rental']
        elif "Initial Rental (excl. VAT)" in data:
            CustomerDeposit = data['Initial Rental (excl. VAT)']
        else:
            CustomerDeposit = 'N/A'

        if "Final Payment" in data:
            OptionalPurchase_FinalPayment = data['Final Payment']
        else:
            OptionalPurchase_FinalPayment = 'N/A'

        duration_of_agreement = data['Contract Term']
        AverageMilesPerYear = data['Annual Mileage'].split("miles")[0]

        # print("resp: ",response.url)
        # # # print("TypeofFinance: ", TypeofFinance)
        # print("data: ", data)
        # input("stop ")

        car_make = 'Nissan'
        item = CarItem()
        item['CarMake'] = car_make
        item['CarModel'] = self.remove_special_char_on_excel(CarModel)
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
        item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
        item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = self.remove_percentage_sign(on_the_road_price)
        # if item['OnTheRoadPrice']:
        #     item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
        item['AmountofCredit'] = 'N/A'
        item['DurationofAgreement']   = self.remove_percentage_sign(duration_of_agreement)
        item['OptionalPurchase_FinalPayment']  = self.remove_gbp(OptionalPurchase_FinalPayment)
        item['TotalAmountPayable'] = 'N/A'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = 'N/A'
        item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
        item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
        item['RetailCashPrice'] = self.remove_gbp(on_the_road_price.replace(",", ""))
        # item['OfferExpiryDate'] = OfferExpiryDate
        item['OfferExpiryDate'] = OfferExpiryDate
        item['WebpageURL'] = weburl
        item['DebugMode'] = self.Debug_Mode
        item['CarimageURL'] = carImgurl
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        if item['MonthlyPayment'] != '' and item['CarModel'] != '':
            yield item

            ######################## PCP Start###############################
            ######################## PCP ###############################
    def parse_item_data(self, response):
        """ Function for parse DATA
        """
        MonthlyPayment = str()
        json_data = json.loads(response.body)

        carImgurl = json_data['images']['detail']['mediumStdRes']
        TypeofFinance = json_data['offerType']

        ############# url making #############
        carID = json_data['id']
        weburl = 'https://www.nissan.co.uk/offers.html#category=Personal+Finance&offerId='+carID+''
        ############# url making #############

        model = json_data['model']['name']
        post_modelName = json_data['applicability']
        CarModel = model +" "+ post_modelName
        offer_text =json_data['legals']['main']['details']
        offerExp = offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        OfferExpiryDate = self.dateMatcher(offerExp)[1]
        # print("data: ", OfferExpiryDate)
        # input("stop 1")

        # if "Offer valid until" in offer_text:
        #     OfferExpiryDate = offer_text.split("Offer valid until ")[1].split("at participating")[0]
        # else:
        #     OfferExpiryDate = 'N/A'

        if "excess mileage" in offer_text:
            ExcessMilageCharge = offer_text.split("excess mileage ")[1].split("p")[0]
        else:
            ExcessMilageCharge = 'N/A'
        # print("offer_text: ", offer_text)
        # input("stop")
        if "data" in json_data['table']:
            quoteItems = json_data['table']['data']

            data = dict()
            for vehicle_data in quoteItems:
                key = vehicle_data['label']
                value = vehicle_data['value']
                data.update({key:value})


            if "On the Road Cash Price" in data:
                on_the_road_price = data['On the Road Cash Price']
            elif "On the Road Cash Price (After PiCG)" in data:
                 on_the_road_price = data['On the Road Cash Price (After PiCG)']
            elif "CV On The Road Price (After PiCG)" in data:
                 on_the_road_price = data['CV On The Road Price (After PiCG)']
            elif "On The Road Price (After PiCG)" in data:
                 on_the_road_price = data['On The Road Price (After PiCG)']
            elif "On The Road Price" in data:
                 on_the_road_price = data['On The Road Price']
            elif "On the Road Cash Price" in data:
                 on_the_road_price = data['On the Road Cash Price']
            else:
                on_the_road_price = 'N/A'

            if "48 Monthly Payments of" in data:
                MonthlyPayment = data['48 Monthly Payments of']
            elif "36 Monthly Payments of" in data:
                MonthlyPayment = data['36 Monthly Payments of']
            elif "24 Monthly Payments of" in data:
                MonthlyPayment = data['24 Monthly Payments of']    
            elif "PCH RENTAL (INC VAT)" in data:
                MonthlyPayment = data['PCH RENTAL (INC VAT)']
            else:
                MonthlyPayment = 'N/A'

            if "Optional Final Payment" in data:
                OptionalPurchase_FinalPayment = data['Optional Final Payment']
            else:
                OptionalPurchase_FinalPayment = 'N/A'
            if "Total Amount Payable" in data:
                TotalAmountPayable = data['Total Amount Payable']
            else:
                TotalAmountPayable = 'N/A'

            if "Duration" in data:
                duration_of_agreement = data['Duration']
            elif "Term" in data:
                duration_of_agreement = data['Term']
            elif "Profile" in data:
                duration_of_agreement = data['Profile']
            else:
                duration_of_agreement = 'N/A'

            if "APR Representative" in data:
                representative_apr = data['APR Representative']
            elif "Representative APR" in data:
                representative_apr = data['Representative APR']
            else:
                representative_apr = 'N/A'

            if "Fixed Rate of Interest (P.A.)" in data:
                rate_of_interest = data['Fixed Rate of Interest (P.A.)']
            elif "Rate Of Interest" in data:
                rate_of_interest = data['Rate Of Interest']
            else:
                rate_of_interest = 'N/A'
            if "Nissan Deposit Contribution" in data:
                RetailerDepositContribution = data['Nissan Deposit Contribution']
            elif "Deposit Contribution" in data:
                RetailerDepositContribution = data['Deposit Contribution']
            else:
                RetailerDepositContribution = 'N/A'

            if "Total Customer Deposit" in data:
                CustomerDeposit = data['Total Customer Deposit']
            elif "Customer Deposit" in data:
                CustomerDeposit = data['Customer Deposit']
            elif "Initial Rental / Deposit" in data:
                CustomerDeposit = data['Initial Rental / Deposit']
            else:
                CustomerDeposit = 'N/A'
            if "Total Amount of Credit" in data:
                AmountOfCredit = data['Total Amount of Credit']
            elif "Total Amount Of Credit" in data:
                AmountOfCredit = data['Total Amount Of Credit']
            else:
                AmountOfCredit = 'N/A'

            if "Annual Mileage" in data:
                AverageMilesPerYear = data['Annual Mileage'].split("miles")[0]
            elif "Mileage PA" in data:
                AverageMilesPerYear = data['Mileage PA'].split("miles")[0]
            else:
                AverageMilesPerYear = 'N/A'

            # Innovation Celebration
            if "Innovation Celebration" in TypeofFinance:
                TypeofFinance = 'Personal Contract Purchase'
            else:
                TypeofFinance = TypeofFinance



            # print("resp: ",response.url)
            # print("TypeofFinance: ", TypeofFinance)
            # print("on_the_road_price: ", on_the_road_price)
            # print("duration_of_agreement: ", duration_of_agreement)
            # print("quoteItems: ", quoteItems)
            # # print("data: ", data)
            # input("stop 1")

            car_make = 'Nissan'
            item = CarItem()
            item['CarMake'] = car_make
            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
            item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
            item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
            item['OnTheRoadPrice'] = self.remove_percentage_sign(on_the_road_price)
            if item['OnTheRoadPrice']:
                item['OnTheRoadPrice'] = item['OnTheRoadPrice']
            item['AmountofCredit'] = self.remove_gbp(AmountOfCredit.replace(",", ""))
            if "months" in duration_of_agreement:
                item['DurationofAgreement']   = duration_of_agreement.split("months")[0]
            elif "Months" in duration_of_agreement:
                item['DurationofAgreement'] = duration_of_agreement.split("Months")[0]
            elif "6+35" in duration_of_agreement:
                item['DurationofAgreement'] = '36'
            else:
                item['DurationofAgreement'] = '37'
            item['OptionalPurchase_FinalPayment']   = self.remove_gbp(OptionalPurchase_FinalPayment.replace(",", ""))
            item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = self.remove_percentage_sign(representative_apr)
            item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(rate_of_interest)
            item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
            item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
            item['RetailCashPrice'] = self.remove_gbp(on_the_road_price.replace(",", ""))
            # item['OfferExpiryDate'] = OfferExpiryDate
            item['OfferExpiryDate'] = OfferExpiryDate
            item['WebpageURL'] = weburl
            item['DebugMode'] = self.Debug_Mode
            item['CarimageURL'] = carImgurl
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            if item['MonthlyPayment'] != '' and item['CarModel'] != '':
                yield item
