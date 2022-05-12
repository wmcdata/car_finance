# -*- coding: utf-8 -*-
from numpy import e
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
import urllib
from datetime import datetime, timedelta
import re
import time
import json

###############PCP AND Contract HIRE BOTH###########################
###############PCP AND Contract HIRE BOTH###########################

class RenaultSpider(BaseSpider):
    name = "renault.co.uk"

    allowed_domains = ['renault.co.uk', 'offers.renault.co.uk']

    start_url = ['http://offers.renault.co.uk/cars', 'https://offers.renault.co.uk/business']
    def __init__(self):
        super(RenaultSpider, self).__init__()


    def start_requests(self):
        for url in self.start_url:
            if "/cars" in url:
                yield Request(url, callback=self.parse_model_url, headers=self.headers)
            else:
            # if "/business" in url:
                yield Request(url, callback=self.parse_ch_model_url, headers=self.headers)

            #######################################################
            #################### CONTRACT HIRE  ###################
            ######################################################

    def parse_ch_model_url(self, response):
        """
        """
        carloop = response.xpath('//div[@class="grid-container"]/div[@class="grid-item"]')
        for href in carloop:
            Premodel = self.getText(href, './/h3/text()')
            url = self.getText(href, './/a[contains(text(), "View offers")]/@href')
            CarimageURL = self.getText(href, './/div/img/@src')
            urls = response.urljoin(url)
            # print("href: ", urls)
            # href = 'https://offers.renault.co.uk/Endpoints/GetInfoCar.ashx?type=contract-hire-36&currentTab=&model=%s' % model
            # print("model: ", model)
            # input("stop")

            if "kangooze_business" in urls or "master_business" in urls or "trafic_business" in urls or "kangoovan_business" in urls or "hirepurchase" in urls or "Trafic-Passenger-business" in urls or "new-master-ze" in urls:
                pass
            else:
                # print("urls: ", urls)
                # input("stop")
                yield Request(urls, callback=self.parse_ch_model, headers=self.headers, meta={"Premodel":Premodel, "CarimageURL":CarimageURL})

    def _find_dict(self, dic, kw, finv=True):
        for k in dic:
            if kw.lower() in k.lower():
                return dic[k]
        if finv:
            for k in dic:
                if kw.lower() in dic[k].lower():
                    return dic[k]
        return ''

    def parse_ch_model(self, response):
        """Business Offers
        """
        # print("resp:: ", response.url)
        # input("stop")
        CarimageURL =  response.meta['CarimageURL']
        PreModel =  response.meta['Premodel']

        PostModel =  self.getTexts(response, '//p[@class="card_name"]/text()')
       
        MonthlyPayment = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "35 Monthly Rentals of")]/following-sibling::td/text()')
        CustomerDeposit = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Advance Payment")]/following-sibling::td/text()')
       
        i = 0
        for x in MonthlyPayment:
            MonthlyPayments = x


            item = CarItem()
            item['CarMake'] = 'Renault'
            try:
                if PostModel != []:
                    item['CarModel'] = self.remove_special_char_on_excel(PreModel +' '+ PostModel[i])
                else:
                    item['CarModel'] = self.remove_special_char_on_excel(PreModel)
            except:
                item['CarModel'] = self.remove_special_char_on_excel(PreModel)
            item['TypeofFinance'] = self.get_type_of_finance('Business Contract Hire')
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayments)
            if item['MonthlyPayment']:
                item['MonthlyPayment'] = float(item['MonthlyPayment'])
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit[i])
            if item['CustomerDeposit']:
                item['CustomerDeposit'] = float(item['CustomerDeposit'])
            item['RetailerDepositContribution'] = 'N/A'

            item['OnTheRoadPrice'] = 'N/A'
            item['OptionalPurchase_FinalPayment'] = 'N/A'

            item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = '36'
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
      
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = "N/A"
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = '6000'
            item['RetailCashPrice'] = 'N/A'
            item['OfferExpiryDate'] = "30/06/2022"
            
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent']  = float()
            item['CarimageURL'] = CarimageURL
            item['WebpageURL'] = response.url
            if item['MonthlyPayment'] != '':
                i += 1
                yield item


        #######################################################
        ###################### PCP  ###########################
        ######################################################


    def parse_model_url(self, response):
        """PCP OFFERS
        """

        carloop = response.xpath('//div[@class="grid-container"]/div[@class="grid-item"]')
        for href in carloop:
            Premodel = self.getText(href, './/h3/text()')
            url = self.getText(href, './/div/a[contains(text(), "View offers")]/@href')
            CarimageURL = self.getText(href, './/div/img/@src')
            urls = response.urljoin(url)
        

            if "personal-contract-hire" in urls:
                href = urls.replace("personal-contract-hire", "selection")
            else:
                href = urls

                # 'https://offers.renault.co.uk/Endpoints/GetInfoCar.ashx?type=selection&currentTab=&model=grandscenic&_=1538566207483'
                # href = 'http://offers.renault.co.uk/Endpoints/GetInfoCar.ashx?type=&currentTab=&model=%s' % model

            # print("href: ", href)
            # print("model: ", model)
            # print("res: ", response.url)
            # input("stop")
            yield Request(href, callback=self.parse_model, headers=self.headers, meta={"Premodel":Premodel, "CarimageURL":CarimageURL})

    def _find_dict(self, dic, kw, finv=True):
        for k in dic:
            if kw.lower() in k.lower():
                return dic[k]
        if finv:
            for k in dic:
                if kw.lower() in dic[k].lower():
                    return dic[k]

        return ''

    def parse_model(self, response):
        """PCP OFFERS
        """
        # print("res: ", response.url)
        # input("stop")
        CarimageURL =  response.meta['CarimageURL']
        PreModel =  response.meta['Premodel']

        PostModel =  self.getTexts(response, '//p[@class="card_name"]/text()')

        Interest = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Fixed interest rate")]/following-sibling::td/text()')
        DurationofAgreement = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Duration")]/following-sibling::td/text()')
        MonthlyPayment = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Monthly payments")]/following-sibling::td/text()')
        CustomerDeposit = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Customer deposit")]/following-sibling::td/text()')
        RetailerDepositContribution = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Renault contribution")]/following-sibling::td/text()')
        OnTheRoadPrice = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Cash price")]/following-sibling::td/text()')
        AmountofCredit = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Total amount of credit")]/following-sibling::td/text()')
        OptionalPurchase_FinalPayment = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Optional final payment")]/following-sibling::td/text()')
        TotalAmountPayable = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Total amount payable")]/following-sibling::td/text()')
        RepresentativeAPR = self.getTexts(response, './/table//tbody[contains(@class, "tbody") or contains(@class, "")]/tr//td[contains(text(), "APR representative")]/text()') ### Difff

        i = 0
        for x in MonthlyPayment:
            MonthlyPayments = x

            # print("mo//del: ", Interest)
            # if RetailerDepositContribution != [] and RetailerDepositContribution != ['']:
            #     print("RetailerDepositContribution: ", RetailerDepositContribution)
            #     # # # # print("mMonthlyPayment: ", PostModel)
            #     # # # # print("mMonthlyPayment: ", PostModel[i])
            #     # print("res: ", response.url)
            #     input("stop")


            item = CarItem()
            item['CarMake'] = 'Renault'
            try:
                if PostModel != []:
                    item['CarModel'] = self.remove_special_char_on_excel(PreModel +' '+ PostModel[i])
                else:
                    item['CarModel'] = self.remove_special_char_on_excel(PreModel)
            except:
                item['CarModel'] = self.remove_special_char_on_excel(PreModel)
            item['TypeofFinance'] = self.get_type_of_finance('PCP')
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayments)
            if item['MonthlyPayment']:
                item['MonthlyPayment'] = float(item['MonthlyPayment'])
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit[i])
            if item['CustomerDeposit']:
                item['CustomerDeposit'] = float(item['CustomerDeposit'])
            try:
                if RetailerDepositContribution != [] and RetailerDepositContribution != ['']: 
                    item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution[i])
                else:
                    item['RetailerDepositContribution'] = 'N/A'
            except:
                item['RetailerDepositContribution'] = 'N/A'
            # if item['RetailerDepositContribution']:
            #     item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
            item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice[i])
            if item['OnTheRoadPrice']:
                item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
            item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment[i])

            item['AmountofCredit'] = self.remove_gbp(AmountofCredit[i])
            item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement[i]).strip()
            item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable[i])
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            if RepresentativeAPR != []:
                item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR[i])
            else:
                item['RepresentativeAPR'] = 'N/A'

            try:
                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(Interest[i])
            except:
                item['FixedInterestRate_RateofinterestPA'] = "N/A"

            item['ExcessMilageCharge'] = '8'
            item['AverageMilesPerYear'] = '6000'
            item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice[i])
            item['OfferExpiryDate'] = "30/06/2022"
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent']  = float()
            item['CarimageURL'] = CarimageURL
            item['WebpageURL'] = response.url
            if item['MonthlyPayment'] != '':
                i += 1
                yield item
