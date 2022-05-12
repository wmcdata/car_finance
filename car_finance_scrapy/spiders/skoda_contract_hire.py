# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
import json
import urllib
from datetime import datetime, timedelta
import re
import time

class SkodaSpider(BaseSpider):
    name = "skoda.contract.hire"
    allowed_domains = ['tools.skoda.co.uk', 'www.skoda.co.uk', 'datahub.skoda.co.uk']
    start_url = 'https://www.skoda.co.uk/car-finance/personal-contract-hire'
    def __init__(self):
        super(SkodaSpider, self).__init__()

    def start_requests(self):
        yield Request(self.start_url, callback=self.parse_car_models, headers=self.headers)

    # def parse_model_url(self, response):
    #     divpath = response.xpath('//div[@class="wrap-page"]//div[@class="items-wrapper"]//div[@class="col-sm-6"]')
    #     for a in divpath:
    #         url = self.getText(a, './/p/strong/a[contains(text(), "VIEW OUR ")]/@href')
    #         href = response.urljoin(url)
    #         # print("href: ", href)
    #         # print("urls: ", response.url)
    #         # input("stop")
    #         yield Request(href, callback=self.parse_car_models, headers=self.headers)

    def parse_car_models(self, response):

        datadiv = response.xpath('//div[@class="items-wrapper"]//div[@class="col-sm-6"]')
        for data in datadiv:
            CarModel = self.getText(data, './/div[@class="paragraph"]//h3/text()')
            CustomerDeposit  = self.getText(data, './/div[@class="paragraph"]//div/p/strong[contains(text(), "Initial Rental")]/following-sibling::text()')
            MonthlyPayment  = self.getText(data, './/div[@class="paragraph"]//div/p/strong[contains(text(), "monthly rentals")]/following-sibling::text()')
            ExcessMilageCharge  = self.getText(data, './/div[@class="paragraph"]//div/p/strong[contains(text(), "Excess mileage charge")]/following-sibling::text()')

            CarImageUrl  = self.getText(data, './/div[@class="responsive-picture-wrapper"]//picture//img/@src')

            offer_exp = self.getTextAll(response, "//p[contains(text(), 'Business users only') or contains(text(), 'Contract Hire agreement')]//text()")
            offerExp = offer_exp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
            if offerExp:
                OfferExpiryDate = self.dateMatcher(offerExp)[0]
            else:
                OfferExpiryDate = 'N/A'

            # if "Ordered by" in offer_exp:
            #     OfferExpiryDate = offer_exp.split("Ordered by")[1].split("from participating")[0]
            # elif "ordered by" in offer_exp:
            #     OfferExpiryDate = offer_exp.split("ordered by")[1].split("from participating")[0]
            # elif "Delivery by " in offer_exp:
            #     OfferExpiryDate = offer_exp.split("Delivery by ")[1].split(". from participating")[0]
            # elif "Until " in offer_exp:
            #     OfferExpiryDate = offer_exp.split("Until ")[1].split(".")[0]
            # else:
            #     OfferExpiryDate = offer_exp

            # print("href: ", CustomerDeposit)
            # print("MonthlyPayment: ", MonthlyPayment)
            # print("OfferExpiryDate: ", OfferExpiryDate)
            # print("urls: ", response.url)
            # input("stop")

            if MonthlyPayment:
                item = CarItem()
                item['CarMake'] = 'Skoda'
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                item['TypeofFinance'] = self.get_type_of_finance('Business Contract Hire')
                item['DurationofAgreement'] = '36'
                item['AverageMilesPerYear'] = 'N/A'
                item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                item['RetailerDepositContribution'] = 'N/A'
                item['OnTheRoadPrice'] = 'N/A'
                item['OptionalPurchase_FinalPayment'] = 'N/A'
                item['AmountofCredit'] = 'N/A'
                item['TotalAmountPayable'] = 'N/A'
                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                item['RepresentativeAPR'] = 'N/A'
                item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                item['OfferExpiryDate'] = OfferExpiryDate
                item['RetailCashPrice'] = 'N/A'
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                item['CarimageURL'] = CarImageUrl
                item['WebpageURL'] = response.url
                if item['CarModel'] != '' and item['MonthlyPayment'] != '':
                    yield item
