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
    name = "london.mclaren.com"
    allowed_domains = []
    holder = list()
    start_url = 'https://london.mclaren.com/en/mclaren-financial-services'
    # start_url = 'https://www.infiniti.co.uk/cars/new-cars/q30/q30-offers.html'
    base_url = 'https://london.mclaren.com/'

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
        # offerExp = self.getText(response, '//p[@class="footnote"]/text()')
        href = self.getTexts(response, '//div[@class="container"]//a/@href')
        for a in href:
            href = urljoin(response.url, a)
            if "/mclaren-financial-services" in href:
                # print("final_url: ", offerExp)
                # input("wait here:")
                yield Request(href, callback=self.parse_item, headers=self.headers)

    def parse_item(self, response):
        """ Function for parse category
        """

        CarimageURL = self.getTextAll(response, '//div/picture//img/@src')
        CarModel = self.getTextAll(response, '//h2[@class="heading-02"]/text()')
        MonthlyPayment = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Monthly Instalments")]/following-sibling::div/text()')

        CustomerDeposit = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Customer Deposit")]/following-sibling::div/text()')

        RepresentativeAPR = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Representitive APR") or contains(text(), "Representative APR")]/following-sibling::div/text()')

        RetailerDepositContribution = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Finance Deposit Contribution")]/following-sibling::div/text()')

        OnTheRoadPrice = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "On The Road Price") or contains(text(), "OTR Price")]/following-sibling::div/text()')

        AmountofCredit = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Amount Of Credit") or contains(text(), "Amount of Credit")]/following-sibling::div/text()')

        FixedInterestRate_RateofinterestPA = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Fixed rate of interest")]/following-sibling::div/text()')

        TotalAmountPayable = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Total Amount Payable") or contains(text(), "Total amount payable")]/following-sibling::div/text()')

        DurationofAgreement = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Duration Of Agreements") or contains(text(), "Duration of agreement")]/following-sibling::div/text()')

        AverageMilesPerYear = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Mileage Per Annum") or contains(text(), "Mileage per annum")]/following-sibling::div/text()')

        OptionalPurchase_FinalPayment = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Optional final payment")]/following-sibling::div/text()')

        ExcessMilageCharge = self.getText(response, '//div[@class="spec-item row"]//div[contains(text(), "Excess mileage charge") or contains(text(), "Excess mileage charge per mile") or contains(text(), "Excess Mileage charge")]/following-sibling::div/text()')


        car_make = "Mclaren London"
        item = CarItem()
        item['CarMake'] = car_make
        item['CarModel'] = self.remove_special_char_on_excel(CarModel)
        item['TypeofFinance'] = self.get_type_of_finance('PCP')
        item['MonthlyPayment'] =self.make_two_digit_no(MonthlyPayment)
        item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
        if RetailerDepositContribution:
            item['RetailerDepositContribution'] = self.remove_percentage_sign(RetailerDepositContribution)
        else:
            item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
        item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
        item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
        item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
        item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
        item['CarimageURL'] = CarimageURL
        item['OfferExpiryDate'] = 'N/A'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = response.url
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        yield item
