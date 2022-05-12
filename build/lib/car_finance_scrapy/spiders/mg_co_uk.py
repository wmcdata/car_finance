# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
import urllib
import json
from datetime import datetime, timedelta
from time import gmtime, strftime
from dateutil.relativedelta import relativedelta
import re
from urllib.parse import urljoin
from html.parser import HTMLParser
from requests import Session
import xmltodict, json
import requests

class MGCar(BaseSpider):
    name = "mg_co_uk"
    allowed_domains = []
    holder = list()
    start_url = 'https://mg.co.uk/offers-finance/'
    base_url = 'https://mg.co.uk/'

    def __init__(self):
        super(MGCar, self).__init__()
        self.i = 0

    def start_requests(self):
        """ Start request
        """
        yield Request( self.start_url, callback=self.parse_pcp_links, headers=self.headers)


    def parse_pcp_links(self, response):
        """ PCP OFFERS
        """
        linkdata = response.xpath('//div[@class="views-element-container"]/ul/li')
        for a in linkdata:
            href = self.getText(a, './/button[contains(text(), "View offers")]/@onclick')
            href = href.split("href='")[1].split("'")[0]
            url = urljoin(response.url, href)
            # print("url", url)
            # input("stop")
            yield Request(url, callback=self.parse_for_data, headers=self.headers)

    # def parse_next_link(self, response):
    #     """ PCP OFFERS
    #     """
    #     linkdata = response.xpath('//section[@id="offers"]//div[@class="offer-inside"]')
    #     for a in linkdata:
    #         href = self.getText(a, './/a/@href')
    #         url = urljoin(response.url, href)
    #         if "pcp" in url:
                # yield Request(url, callback=self.parse_for_data, headers=self.headers)

    def parse_for_data(self, response):
        """ PCP OFFERS here
        """
        # print("url", response.url)
        # input
        # offerExp = self.getText(response, '//div[@class="section-body"]//div//p[strong[contains(text(), "Terms and Conditions")]]/following-sibling::p/span/text()')
        # offerExp = offerExp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        # OfferExpiryDate = self.dateMatcher(offerExp)[1]
        OfferExpiryDate = '30/06/2022'
        CarimageURL = self.getText(response, '//picture/source/@srcset')
        i = 0
        carModel = self.getTexts(response, '//table//thead/tr//th[contains(text(), "Model")]/following-sibling::th/text()')
        MonthlyPayment = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Monthly Payments of") or contains(text(), "Monthly Instalments")]/following-sibling::td/text()')
        OnTheRoadPrice = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "On-The-Road") or contains(text(), "On the road price")]/following-sibling::td/text()')
        CustomerDeposit = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Customer Deposit") or contains(text(), "Customer deposit")]/following-sibling::td/text()')
        AmountofCredit = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Total Amount of Credit") or contains(text(), "Amount of Credit")]/following-sibling::td/text()')
        TotalAmountPayable = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Total Amount Payable")]/following-sibling::td/text()')
        FixedInterestRate_RateofinterestPA = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Fixed Rate of Interest") or contains(text(), "Fixed Rate of interest")]/following-sibling::td/text()')
        AnnualMileage = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Mileage Per Annum") or contains(text(), "Mileage per Annum")]/following-sibling::td/text()')
        ExcessMilageCharge = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Excess Mileage Charge")]/following-sibling::td/text()')
        DurationofAgreement = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Duration of Agreement")]/following-sibling::td/text()')
        RepresentativeAPR = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Representative APR")]/following-sibling::td/text()')
        OptionalPurchase_FinalPayment = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Optional Final Payment")]/following-sibling::td/text()')
        RetailerDepositContribution = self.getTexts(response, '//table//tbody/tr//td[contains(text(), "Finance Deposit Contribution")]/following-sibling::td/text()')

        # print("item", carModel)
        # print("MonthlyPayment", MonthlyPayment)
        # print("OnTheRoadPrice", OnTheRoadPrice)
        # print("CustomerDeposit", CustomerDeposit)
        # print("AmountofCredit", AmountofCredit)
        # print("TotalAmountPayable", TotalAmountPayable)
        # print("FixedInterestRate_RateofinterestPA", FixedInterestRate_RateofinterestPA)
        # # print("offerExp", offerExp)
        # print("item", response.url)
        # input("stop")

        for x in MonthlyPayment:
            MonthlyPayments = x
            item = CarItem()
            item['CarMake'] = 'MG'
            item['CarModel'] = self.remove_special_char_on_excel(carModel[i])
            item['TypeofFinance'] = self.get_type_of_finance("PCP")
            item['MonthlyPayment'] = self.make_two_digit_no(self.reText(MonthlyPayments, r'([\d\.\,]+)'))
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit[i])
            item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution[i])
            item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice[i])
            item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment[i])
            item['AmountofCredit'] = self.remove_gbp(AmountofCredit[i])
            item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement[i])
            item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable[i])
            item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
            item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR[i])
            item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA[i])
            item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge[i])
            item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage[i])
            item['OfferExpiryDate'] = OfferExpiryDate
            item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice[i])
            item['CarimageURL'] = CarimageURL
            item['WebpageURL'] = response.url
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            i += 1
            yield item
