# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
# from scrapy import log
import urllib
import json
from datetime import datetime, timedelta
from time import gmtime, strftime
from dateutil.relativedelta import relativedelta
import re
from urllib.parse import urljoin
### Update 12-9-2019
class MercedesVans(BaseSpider):
    name = "mercedes.benz.vans"
    allowed_domains = []
    holder = list()
    base_url  = 'https://www.mercedes-benz.co.uk/'
    start_url = 'https://www.mercedes-benz.co.uk/vans/en/offers-and-finance/latest-offers'

    def __init__(self):
        super(MercedesVans, self).__init__()


    def start_requests(self):
        """ Start request
        """
        yield Request(self.start_url, callback=self.parse_vans_url, headers=self.headers)

    def parse_vans_url(self, response):
        """ Function for vanz url
        """
        link_path = response.xpath('//div[@class="main-parsys parsys"]//a[@class="vans_image-teaser--half"]')
        for a in link_path:
            # CarimageURL = response.urljoin(self.getText(a, './/div[@class="vans_gallery__wrapper"]//span/@data-src-mq3'))
            url = self.getText(a, './@href')
            href = response.urljoin(url)
            # vans_headline = self.getText(a, './/h2[@class="vans_image-teaser__headline"]/text()') ### USEABLE
            if "/approved-used" not in href:
                # print("url", href)
                # input("wait")
                yield Request(href, callback=self.parse_vans_items_Data, headers=self.headers, dont_filter=True)


    def parse_vans_items_Data(self, response):
        """ Function for parse item
        """
        # CarimageURL = response.meta['CarimageURL']
        data_path = response.xpath('//div[@class="main-parsys parsys"]//div[@class="vans_offer-multi__content-wrapper"]')
        for table in data_path:
            vansModel = self.getText(table, './/h3[@class="vans_offer__subheadline"]/b/text()')
            if not vansModel:
                vansModel = self.getText(table, './/h3[@class="vans_offer__subheadline"]/text()')
            CustomerDeposit = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Advance Rental") or contains(text(), "Customer Deposit Inc.") or contains(text(), "Customer Deposit inc") or contains(text(), "Customer Deposit")]/following-sibling::td/text()')
            if len(CustomerDeposit) == 1:
                CustomerDeposit = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Advance Rental") or contains(text(), "Customer Deposit Inc.") or contains(text(), "Customer Deposit inc") or contains(text(), "Customer Deposit")]/following-sibling::td/b/text()')
            if not CustomerDeposit:
                CustomerDeposit = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Advance Rental") or contains(text(), "Customer Deposit Inc.") or contains(text(), "Customer Deposit inc") or contains(text(), "Customer Deposit")]/following-sibling::td/i/text()')

            RetailerDepositContribution = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Rental Contribution") or contains(text(), "Finance Deposit Contribution")]/following-sibling::td/text()')
            if len(RetailerDepositContribution) == 1:
                RetailerDepositContribution = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Rental Contribution") or contains(text(), "Finance Deposit Contribution")]/following-sibling::td/b/text()')

            MonthlyPayment = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Monthly Rental") or contains(text(), "Monthly Payment")]/following-sibling::td/text()')
            if len(MonthlyPayment) == 1:
                MonthlyPayment = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Monthly Rental") or contains(text(), "Monthly Payment")]/following-sibling::td/b/text()')

            ExcessMilageCharge = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Excess Mileage Charge")]/following-sibling::td/text()')

            CarimageURL = self.getText(table, './/div[@class="vans_offer__image"]//picture/img[contains(@class, "vans_image__image")]/@src')

            # if "https://www.mercedes-benz.co.uk/vans/en/offers-and-finance/latest-offers/conversions-offers" in response.url:
            #     print("vansModel", vansModel)
            #     print("MonthlyPayment", len(MonthlyPayment))
            #     print("MonthlyPayment", MonthlyPayment)
            #     print("res", response.url)
            #     input("wait")

            # OnTheRoadPrice = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "On-the-road Price")]/following-sibling::td/text()')
            # OptionalPurchase_FinalPayment = self.getText(table, './/div[@class="vans_offer__table"]/table/tbody/tr/th[contains(text(), "Optional Final Payment")]/following-sibling::td/text()')

            # text_paragraph = self.getText(table, './/div[@class="vans_disclaimer__copy"]/text()')
            # if "Offer ends" in text_paragraph:
            #     OfferExpiryDate = text_paragraph.split("Offer ends")[1].split(".")[0]
            # else:
            #     OfferExpiryDate = 'N/A'

            # text_paragraph = self.getTextAll(table, './/table/tbody/tr/th[contains(text(), "year lease on Contract Hire")]/text()')

            # print("url", response.url)
            # print("vansModel", text_paragraph)
            # input()

            # print("CustomerDeposit", CustomerDeposit)
            # print("RetailerDepositContribution", RetailerDepositContribution)
            # print("MonthlyPayment", MonthlyPayment)
            # print("OnTheRoadPrice", OnTheRoadPrice)
            # print("text_paragraph", matches)
            # input("wait")
            if "eVito Tourer" in vansModel:
                DurationofAgreement = '48'
            else:
                DurationofAgreement = '36'



            car_make = "Mercedes-Benz"
            item = CarItem()
            item['CarMake'] = car_make
            item['CarModel'] = self.remove_special_char_on_excel(vansModel)
            item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
            item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
            item['OnTheRoadPrice'] = item['RetailCashPrice'] = 'N/A'
            item['AmountofCredit'] = 'N/A'
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
            item['AverageMilesPerYear'] = 'N/A'
            item['DurationofAgreement'] = DurationofAgreement
            item['TypeofFinance'] = "Commercial Contract Hire"
            # item['OfferExpiryDate'] = OfferExpiryDate'
            item['OfferExpiryDate'] = "30/06/2022"
            item['CarimageURL'] = CarimageURL
            item['WebpageURL'] = response.url
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            if item['MonthlyPayment'] != "":     
                yield item

    # def list_to_dict(self, key, value):
    #     lenth_of_keys = len(key)
    #     lenth_of_values = len(value)
    #     divident = int(lenth_of_values/lenth_of_keys)
    #     values = list(self.chunks(value, divident))
    #     a=[]
    #     count=0
    #     for _ in range(divident):
    #         count_inner = 0
    #         for val in values:
    #             try:
    #                 dic = dict([(key[count_inner],val[count])])
    #             except:
    #                 pass
    #             a.append(dic)
    #             count_inner +=1
    #         count +=1
    #     a = list(self.chunks(a, lenth_of_keys))
    #     return a
    # def chunks(self, l, n):
    #     count_inner = 0
    #     for i in range(0, len(l), n):
    #         # print("count_inner in chunks: ", count_inner)
    #         # input("wait here:")
    #         count_inner +=1
    #         yield l[i:i+n]
