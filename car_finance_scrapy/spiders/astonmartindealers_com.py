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


class InfinitiSpider(BaseSpider):
    name = "astonmartindealers.com"
    allowed_domains = []
    holder = list()
    start_url = 'https://www.astonmartin.com/en-gb/models'
    # start_url = 'https://www.infiniti.co.uk/cars/new-cars/q30/q30-offers.html'
    base_url = 'http://newportpagnell.astonmartindealers.com'

    def __init__(self):
        super(InfinitiSpider, self).__init__()
        self.i = 0

    def start_requests(self):
        """ Start request
        """
        yield Request(self.start_url, callback=self.parse_category, headers=self.headers)

    def parse_category(self,response):
        """ Start Category
        """
        href = self.getTexts(response, '//nav[@class="model-nav"]/div[@class="sub-nav-container"]/ul/li/a/@href')
        for a in href:
            href = urljoin(response.url, a)
            # print("href: ", href)
            # input("wait here:")
            yield Request(href, callback=self.parse_item, headers=self.headers)

    def parse_item(self, response):
        """ Function for parse category
        """

        carModel = self.getText(response, '//h2[@class="big-header-text"]//span/text()')

        JsonRequestData = self.getTextAll(response, '//script[contains(@id, "financialServicesBlock-")]//text()')
        if JsonRequestData:
            jsonResponse = json.loads(JsonRequestData)[0]
            carImage = jsonResponse['image']['src'][0]['srcset']
            termsLink = jsonResponse['termsLink']['url']
            # print("JsonRequestData: ", jsonResponse)
            # input("wait here:")
            data = dict()
            details = jsonResponse['details']
            # print("details",details)
            # input("wait for detail")
            for carData in details:
                label = carData['label']
                value = carData['value']
                data.update({label:value})
            DurationofAgreement = data['Term of Agreement']
            # print("data",data)
            # print("URL",response.url)
            # input("wait for data")
            OnTheRoadPrice = data['On the road cash price']
            try:
                RetailerDepositContribution = data['Deposit Contribution']
            except:
                RetailerDepositContribution ="N/A"
            AmountofCredit = data['Amount Of Credit']
            OptionalPurchase_FinalPayment = data['Optional final payments']
            FixedInterestRate_RateofinterestPA = data['Rate of interest']
            try:
                MonthlyPayment = data['35 monthly payments']
            except:
                MonthlyPayment = data['35 Monthly Payments']
            try:
                CustomerDeposit = data['Customer deposit']
            except:
                CustomerDeposit = "N/A"
            TotalAmountPayable = data['Total amount payable']
            RepresentativeAPR = data['Representative APR']

            # print("JsonRequestData: ", data)
            # input("wait here:")

            car_make = "Aston Martin "
            item = CarItem()
            item['CarMake'] = car_make
            item['CarModel'] = "Aston Martin"+' '+ self.remove_special_char_on_excel(carModel)
            item['TypeofFinance'] = self.get_type_of_finance('PCP')
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)

            try:
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
            except:
                item['CustomerDeposit'] = CustomerDeposit

            try:
                item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
            except:
                item['RetailerDepositContribution'] = RetailerDepositContribution
            item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
            item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
            item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
            if DurationofAgreement:
                item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
            else:
                item['DurationofAgreement'] = 'N/A'
            item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
            item['OptionToPurchase_PurchaseActivationFee'] =  'N/A'
            item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
            if FixedInterestRate_RateofinterestPA:
                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
            else:
                item['FixedInterestRate_RateofinterestPA'] = 'N/A'

            item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
            item['CarimageURL'] = carImage
            item['OfferExpiryDate'] = 'N/A'
            item['DebugMode'] = self.Debug_Mode
            item['WebpageURL'] = response.url
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            href = urljoin(response.url, termsLink)
            yield Request(href, callback=self.parse_for_exc_avg_mill, headers=self.headers, meta={"item":item})

    def parse_for_exc_avg_mill(self, response):
        """ Function for Terms data
        """
        item = response.meta['item']
        TermsData = self.getText(response, '//h1[contains(text(), "Terms and conditions")]/following-sibling::p/text()')
        AverageMilesPerYear = TermsData.split("contract mileage")[1].split("miles")[0]
        ExcessMilageCharge = TermsData.split("excess mileage")[1].split("p")[0]
        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
        item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
        # print("TermsData: ", TermsData)
        # input("wait here:")
        yield item
