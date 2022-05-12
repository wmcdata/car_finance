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


class BmwSpider(BaseSpider):
    name = "offers.bmw.co.uk"
    allowed_domains = []
    holder = list()
    start_url = 'https://offers.bmw.co.uk/finance-offers/?filters%5BProductFamily%5D=PCP&filters%5BvalidOn%5D=false'
    base_url = 'https://offers.bmw.co.uk/'

    def __init__(self):
        super(BmwSpider, self).__init__()
        self.i = 0

    def start_requests(self):
        """ Start request
        """
        session = Session()
        session.head('https://offers.bmw.co.uk/finance-offers/')

        response_pch = session.post(
        url='https://offers.bmw.co.uk/finance-offers/?filters%5BProductFamily%5D=PCH&filters%5BvalidOn%5D=false',
        headers={
        'Referer': 'https://offers.bmw.co.uk/finance-offers/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type':'application/json; charset=UTF-8',
        'X-Requested-With':'XMLHttpRequest'
        }
        )

        cars_pch = json.loads(response_pch.text)

        for car in cars_pch['offers']:
            quotereference = car['quotereference']
            offercode = car['offercode']
            offertitle = car['offertitle']

            # print("offercode", offercode)
            # print("offertitle", offertitle)
            # # print("uirl", response.url)
            # input("wait")
            # offer_date = car['validto']
            car_make = "BMW"
            # ajax_url = "https://services.codeweavers.net/api/BMW/QuoteData?ApiKey=vF66dG3LOZEvuM4d57&QuoteReference="+quotereference+"&Referrer=https:%2F%2Foffers.bmw.co.uk%2F&SystemKey=BMW"

            ajax_url = "https://services.codeweavers.net/api/BMW/QuoteData?ApiKey=vF66dG3LOZEvuM4d57&QuoteReference="+quotereference+"&Referrer=https:%2F%2Foffers.bmw.co.uk%2Ffinance-offers%2Fresult%2F%3FofferCode%3D"+offercode+"&SystemKey=BMW"
            car_url = "https://offers.bmw.co.uk/finance-offers/result/?offerCode="+offercode

            yield Request(car_url, callback=self.get_image, headers=self.headers, meta={'ajax_url': ajax_url})

        response_hp = session.post(
        url='https://offers.bmw.co.uk/finance-offers/?filters%5BProductFamily%5D=HP&filters%5BvalidOn%5D=false',
        headers={
        'Referer': 'https://offers.bmw.co.uk/finance-offers/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type':'application/json; charset=UTF-8',
        'X-Requested-With':'XMLHttpRequest'
        }
        )

        cars_hp = json.loads(response_hp.text)

        for car in cars_hp['offers']:

            quotereference = car['quotereference']
            # print("cars_pch", quotereference)
            # # print("uirl", response.url)
            # input("wait")
            offercode = car['offercode']
            offertitle = car['offertitle']

            # print("offercode", offercode)
            # print("offertitle", offertitle)
            # # print("uirl", response.url)
            # input("wait")
            car_make = "BMW"

            # ajax_url = "https://services.codeweavers.net/api/BMW/QuoteData?ApiKey=vF66dG3LOZEvuM4d57&QuoteReference="+quotereference+"&Referrer=https:%2F%2Foffers.bmw.co.uk%2F&SystemKey=BMW"
            ajax_url = "https://services.codeweavers.net/api/BMW/QuoteData?ApiKey=vF66dG3LOZEvuM4d57&QuoteReference="+quotereference+"&Referrer=https:%2F%2Foffers.bmw.co.uk%2Ffinance-offers%2Fresult%2F%3FofferCode%3D"+offercode+"&SystemKey=BMW"
            car_url = "https://offers.bmw.co.uk/finance-offers/result/?offerCode="+offercode

            yield Request(car_url, callback=self.get_image, headers=self.headers, meta={'ajax_url': ajax_url})

        response_pcp = session.post(
        url='https://offers.bmw.co.uk/finance-offers/?filters%5BProductFamily%5D=PCP&filters%5BvalidOn%5D=false',
        headers={
        'Referer': 'https://offers.bmw.co.uk/finance-offers/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type':'application/json; charset=UTF-8',
        'X-Requested-With':'XMLHttpRequest'
        }
        )

        cars_pcp = json.loads(response_pcp.text)

        for car in cars_pcp['offers']:

            quotereference = car['quotereference']
            offercode = car['offercode']
            offertitle = car['offertitle']
            car_make = "BMW"
            # ajax_url = "https://services.codeweavers.net/api/BMW/QuoteData?ApiKey=vF66dG3LOZEvuM4d57&QuoteReference="+quotereference+"&Referrer=https:%2F%2Foffers.bmw.co.uk%2F&SystemKey=BMW"

            ajax_url = "https://services.codeweavers.net/api/BMW/QuoteData?ApiKey=vF66dG3LOZEvuM4d57&QuoteReference="+quotereference+"&Referrer=https:%2F%2Foffers.bmw.co.uk%2Ffinance-offers%2Fresult%2F%3FofferCode%3D"+offercode+"&SystemKey=BMW"
            car_url = "https://offers.bmw.co.uk/finance-offers/result/?offerCode="+offercode

            yield Request(car_url, callback=self.get_image, headers=self.headers, meta={'ajax_url': ajax_url})


    def get_image(self, response):

        CarImageUrl = response.xpath('//div[@class="container"]//div[@class="col-md-5"]/img/@src').extract()
        ajax_url = response.meta['ajax_url']
        # print("ajax_url", ajax_url)
        # # print("offertitle", offertitle)
        # # print("uirl", response.url)
        # input("wait")
        yield Request(ajax_url, callback=self.parse_pcp_item, headers=self.headers_ajax, meta={'CarImageUrl': CarImageUrl, 'car_url': response.url})


    def parse_pcp_item(self, response):
        """ Function for parse category
        """

        JO = json.loads(response.body)

        car_model = JO['Vehicle']['Description']
        car_make = "BMW"
        type_of_finance = JO['Quote']['ProductType']
        monthly_payment = JO['Quote']['RegularPayment']
        customer_deposit = JO['Quote']['CashDeposit']
        retailer_deposit_contributions = JO['Quote']['DepositContributions']
        retailer_deposit_contribution = float()
        # print("uirl", response.url)
        # print("type_of_finance", type_of_finance)
        # print("JO", JO)
        # print("uirl", response.url)
        # input("wait")
        for key in retailer_deposit_contributions:
            retailer_deposit_contribution = retailer_deposit_contribution + float(key['Amount'])

        balance = float(JO['Quote']['Balance'])
        total_deposit = float(JO['Quote']['TotalDeposit'])
        on_the_road_price = float(balance + total_deposit)
        final_payment = JO['Quote']['FinalPayment']
        amount_of_credit = balance
        duration_of_agreement = JO['Quote']['Term']
        total_amount_payable = JO['Quote']['TotalAmountPayable']
        purchase_activation_fee = JO['Quote']['Fees']
        ContentExp = JO['TermsAndConditions']
        offerExp = ContentExp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        OfferExpiryDate = self.dateMatcher(offerExp)[1]

        # if "ordered between " in OfferExpiryDate:
        #     OfferExpiryDate = OfferExpiryDate.split("ordered between ")[1]
        #     OfferExpiryDate = OfferExpiryDate.split("and")[1].split(",")[0]
        # else:
        #     OfferExpiryDate = str()
        # if " and registered by" in OfferExpiryDate:
        #     OfferExpiryDate = OfferExpiryDate.split(" and registered by")[0]
        #     OfferExpiryDate = OfferExpiryDate.split("and")[1]
        #

        # print("JO", JO)
        # print("type_of_finance", type_of_finance)
        # print("model: ", car_model)
        # print("json url: ", response.url)
        # print("url:", response.meta['car_url'])
        # input("wait")

        PurchaseActivationFee = int()
        for fee in purchase_activation_fee:
            PurchaseActivationFee = fee['Amount']
        representative_apr = JO['Quote']['Apr']
        fixed_intrest_rate = JO['Quote']['RateOfInterest']
        excess_milage_charge= JO['Quote']['ExcessMileageRate']
        average_miles_per_year = JO['Quote']['AnnualMileage']
        retail_cash_price = on_the_road_price


        item = CarItem()
        item['CarMake'] = car_make
        item['CarModel'] = self.remove_special_char_on_excel(car_model)
        item['TypeofFinance'] = self.get_type_of_finance(type_of_finance)
        item['MonthlyPayment'] = self.make_two_digit_no(str(monthly_payment))
        if item['MonthlyPayment']:
            item['MonthlyPayment'] = float(item['MonthlyPayment'])
        item['CustomerDeposit'] = self.make_two_digit_no(str(customer_deposit))
        if item['CustomerDeposit']:
            item['CustomerDeposit'] = (item['CustomerDeposit'])
        if "Contract Hire" in item['TypeofFinance']:
            item['RetailerDepositContribution'] = ''
        else:
            item['RetailerDepositContribution'] = retailer_deposit_contribution
            if item['RetailerDepositContribution']:
                item['RetailerDepositContribution'] = (item['RetailerDepositContribution'])
        item['OnTheRoadPrice'] = on_the_road_price
        if item['OnTheRoadPrice']:
            item['OnTheRoadPrice'] = (item['OnTheRoadPrice'])
        item['AmountofCredit'] = amount_of_credit
        item['DurationofAgreement']   = self.remove_percentage_sign(str(duration_of_agreement))
        item['OptionalPurchase_FinalPayment']   = final_payment
        item['TotalAmountPayable'] = total_amount_payable
        item['OptionToPurchase_PurchaseActivationFee'] = self.remove_percentage_sign(str(PurchaseActivationFee))
        item['RepresentativeAPR'] = self.remove_percentage_sign(str(representative_apr))
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(str(fixed_intrest_rate))
        item['ExcessMilageCharge'] = self.remove_percentage_sign(str(excess_milage_charge))
        if "Hire Purchase" in item['TypeofFinance']:
            item['AverageMilesPerYear'] = 'N/A'
        else:
            item['AverageMilesPerYear'] = self.remove_percentage_sign(str(average_miles_per_year))
        item['RetailCashPrice'] = retail_cash_price
        item['OfferExpiryDate'] = OfferExpiryDate
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = response.meta['car_url']
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = ''
        try:
            item['CarimageURL'] = response.meta['CarImageUrl'][0]
        except IndexError:
            item['CarimageURL'] = response.meta['CarImageUrl']
        yield item
