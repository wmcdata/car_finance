# -*- coding: utf-8 -*-
from typing import Optional
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



class DaciaCar(BaseSpider):
    name = "dacia_co_uk"
    allowed_domains = []
    holder = list()
    start_url = 'https://www.dacia.co.uk/offers.html'
    base_url = 'https://www.dacia.co.uk/'

    def __init__(self):
        super(DaciaCar, self).__init__()
        self.i = 0

    def start_requests(self):
        """ Start request
        """
        yield Request(self.start_url, callback=self.parse_for_offers_link, headers=self.headers)

    def parse_for_offers_link(self, response):
        """ PCP OFFERS
        """
        dataloop = response.xpath('//div[@class="ContentCard Slice__element"]')
        for data in dataloop:
            carName = self.getText(data, './/h2[@class="ContentCard__title"]/text()')
            href = self.getText(data, './/figure/div/a/@href')
            # print(carName)
            # print(href)
            # input()
            # dacia-selections
            # personal-contract-hire
            yield Request(href, callback=self.parse_offers_data, headers=self.headers)


    def parse_offers_data(self, response):
        """ PCP OFFERS
        """
        if "personal-contract-hire" in response.url:
            link = response.url.split("?offer")[0]
            weblnk = link.replace("personal-contract-hire", "dacia-selections")
            # print("weblnk", weblnk)
            # print("url", response.url)
            # input("wait")
            yield Request(weblnk, callback=self.parse_offers_data, headers=self.headers, dont_filter=True)
        else:
            # print(response.url)
            # input("top")
                
            carImage = self.getTexts(response, '//img[@class="card_image"]/@src')

            CarModelPre = self.getText(response, '//div[@class="title-page__name"]/h1/text()')
            CarModelPost = self.getTexts(response, '//p[@class="card_name"]/text()')


            Monthlypayments = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "48 monthly payments of")]/following-sibling::td/text()')
            CustomerDeposit = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Customer deposit")]/following-sibling::td/text()')
            OnTheRoadPrice = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Cash price")]/following-sibling::td/text()')
            Duration = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Duration")]/following-sibling::td/text()')
            AmountOfCredit = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/text()')
            OptionalFinalPayment = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Optional final payment")]/following-sibling::td/text()')
            TotalAmountPayable = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/text()')
            FixedInterestRate_RateofinterestPA = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Fixed interest rate p.a.")]/following-sibling::td/text()')
            RepresentativeAPR = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Representative APR")]/following-sibling::td/text()')
            RetailerDepositContribution = self.getTexts(response, '//div[contains(@class, "car-table_home")]/table//tbody/tr/td[contains(text(), "Dacia deposit contribution")]/following-sibling::td/text()')
            
            i = 0
            for x in Monthlypayments:
                MonthlyPayment = x

                # print("CarModelPost;", CarModelPost)
                # print("resp;", response.url)
                # input("stop")
        

                item = CarItem()
                item['CarMake'] = 'Dacia'
                item['CarModel'] = self.remove_special_char_on_excel(CarModelPre+' '+CarModelPost[i])
                item['TypeofFinance'] = self.get_type_of_finance("PCP")
                item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit[i])
                # item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution[i])
                ###################################     05 October 2021     ###################################
                try:
                    item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution[i])
                except:
                    item['RetailerDepositContribution'] = "N/A"
                
                ###################################     05 October 2021     ###################################
                item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice[i])
                item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalFinalPayment[i])
                item['AmountofCredit'] = self.remove_gbp(AmountOfCredit[i])
                item['DurationofAgreement'] = self.remove_percentage_sign(Duration[i])
                item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable[i])
                item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
                item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR[i])
                try:
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA[i])
                except:
                    item['FixedInterestRate_RateofinterestPA'] = 'N/A'    
                item['ExcessMilageCharge'] = "8"
                item['AverageMilesPerYear'] = "6000"
                item['OfferExpiryDate'] = '30/06/2022'
                item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice[i])
                item['CarimageURL'] = 'https://offers.dacia.co.uk/'+carImage[i]
                item['WebpageURL'] = response.url
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                i += 1    
                yield item


            