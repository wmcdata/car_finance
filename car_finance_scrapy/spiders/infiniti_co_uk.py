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
    name = "infiniti.co.uk"
    allowed_domains = []
    holder = list()
    start_url = 'https://www.infiniti.co.uk/offers.html'
    # start_url = 'https://www.infiniti.co.uk/cars/new-cars/q30/q30-offers.html'
    base_url = 'https://www.infiniti.co.uk'

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
        href = self.getTexts(response, '//div[@class="grid-row"]//div[@class="content-group"]/a[contains(text(), "Discover our")]/@href')

        for a in href:
            url = self.base_url+a
            # print("url: ", url.split(".html")[0].split("/")[-1])
            # print("start_url: ", starts_url.split(".html")[0])
            # print("final_url: ", url)
            # input("wait here:")
            yield Request(url, callback=self.parse_item, headers=self.headers)

    #         yield Request(self.final_url, callback=self.parse_item, headers=self.headers)
    #
    def parse_item(self, response):
        """ Function for parse category
        """
        car_model = self.getText(response, '//div[@class="heading-group"]/h2/span[not(contains(text(),"Offers"))]/text()')
        car_images = self.getText(response, '//div[@class="c_029"]/figure/picture//img/@src')

        monthly_payment = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "36")) or (starts-with(text(), "48")) or (starts-with(text(), "24")) or (contains(text(), "Monthly Payments")))]/following-sibling::td//text()')
        on_the_road_price = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "On the")) or (contains(text(), "road cash price")))]/following-sibling::td//text()')
        customer_deposit = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "Customer")) or (contains(text(), "Deposit")) or (contains(text(), "Customer Deposit")) )]/following-sibling::td//text()')
        deposit_contribution = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "INFINITI")) or (contains(text(), " Deposit Contribution")) or (contains(text(), "Dealer Deposit Contribution")))]/following-sibling::td//text()')
        amount_of_credit = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "Amount")) or (contains(text(), " of Credit")) or (contains(text(), "Amount of Credit")))]/following-sibling::td//text()')
        Optional_final_payment = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "Optional")) or (contains(text(), " Final Payment")) or (contains(text(), "Optional Final Payment")))]/following-sibling::td//text()')
        Total_amount_payable = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "Total Amount Payable")) or (contains(text(), " Amount Payable")))]/following-sibling::td//text()')
        duration_of_agreement = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "Duration")) or (contains(text(), "Duration of Agreement")))]/following-sibling::td/text()')
        duration_of_agreement =  duration_of_agreement.split("Months")[0]
        rate_of_intrest = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "Rate")) or (contains(text(), "Interest")) or (contains(text(), "of Interest (per annum) fixed")))]/following-sibling::td//text()')
        APR = self.getText(response, './/div[@class="c_153"]//table/tbody/tr/td[((starts-with(text(), "APR")) or (contains(text(), " Representative")))]/following-sibling::td//text()')
        ### Expiry date Offer ###
        offer_expiry_date = self.getTextAll(response,'//div[@class="custom-font"]/p/b/text()')
        if offer_expiry_date:
            expiry_date = offer_expiry_date.split("-")[1]
            OfferExpiryDate = expiry_date.split("(")[0]
        else:
            OfferExpiryDate = 'N/A'
        ### Expiry date Offer ###

        ### excess Milliage charge ###
        # excess_milliage_charge = self.getText(response,'//div[@class="custom-font"]/p[contains(text(), "Excess Mileage charged")]/text()')
        # if not excess_milliage_charge:
        #     excess_milliage_charge = response.xpath('//div[@class="custom-font"]/p/text()').extract()[3]
        Excess_mil = self.getTextAll(response,'//div[@class="custom-font"]/p/text()')
        if 'Excess Mileage charged at' in Excess_mil:
            Excess_Mileage = Excess_mil.split("Excess Mileage charged at")[1]
            ExcessMilageCharge = Excess_Mileage.split("p")[0]
        else:
            ExcessMilageCharge = 'N/A'
        ### excess Milliage charge ###


        # print("response: ", response.url)
        # print("monthly_payments: ", monthly_payment)
        # print("on_the_road_price: ", on_the_road_price)
        # print("customer_deposit: ", customer_deposit)
        # print("deposit_contribution: ", deposit_contribution)
        # print("amount_of_credit: ", amount_of_credit)
        # print("Optional_final_payment: ", Optional_final_payment)
        # print("Total_amount_payable: ", Total_amount_payable)
        # print("duration_of_agreement: ", duration_of_agreement)
        # print("rate_of_intrest: ", rate_of_intrest)
        # print("APR: ", APR)
        # print("offer_expiry_date: ", expiry_date)
        # print("car_images: ", car_images)
        # print("excess_milliage_charge: ", excess_milliage_charge)
        # print("car_model: ", car_model)
        # input("wait here:")

        car_make = "INFINITI"
        item = CarItem()
        item['CarMake'] = car_make
        item['CarModel'] = self.remove_special_char_on_excel(car_model)
        item['TypeofFinance'] = self.get_type_of_finance('PCP')
        item['MonthlyPayment'] =self.remove_gbp(monthly_payment)
        item['CustomerDeposit'] = self.remove_gbp(customer_deposit)
        item['RetailerDepositContribution'] = self.remove_gbp(deposit_contribution)
        item['OnTheRoadPrice'] = self.remove_gbp(on_the_road_price)
        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(Optional_final_payment)
        item['AmountofCredit'] = self.remove_gbp(amount_of_credit)
        item['DurationofAgreement'] = duration_of_agreement
        item['TotalAmountPayable'] = self.remove_gbp(Total_amount_payable)
        item['OptionToPurchase_PurchaseActivationFee'] = ''
        item['RepresentativeAPR'] = APR
        item['FixedInterestRate_RateofinterestPA'] = rate_of_intrest
        item['ExcessMilageCharge'] = ExcessMilageCharge
        item['AverageMilesPerYear'] = "6000"
        item['RetailCashPrice'] = self.remove_gbp(on_the_road_price)
        item['CarimageURL'] = car_images
        item['OfferExpiryDate'] = OfferExpiryDate
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = response.url
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        if item['MonthlyPayment'] != "":
            yield item
