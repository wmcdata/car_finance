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
from w3lib.http import basic_auth_header

class AudiSpider(BaseSpider):
    name = "audi.co.uk"

    allowed_domains = ['audi.co.uk']
    base_url  = 'https://www.audi.co.uk'

    start_url = ['https://www.audi.co.uk/uk/web/en/find-and-buy/finance-and-offers/own-an-audi.html', 'https://www.audi.co.uk/uk/web/en/find-and-buy/finance-and-offers/lease-an-audi.html']

    headers = {
        
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Proxy-Authorization': basic_auth_header('watchmycompetitor', 'dmt276gnw845')
    }


    def __init__(self):
        super(AudiSpider, self).__init__()

    def start_requests(self):
        for url in self.start_url:
            if "own-an-audi" in url:
                # print("res: ", url)
                # input("stop")
                # yield Request(url, callback=self.parse_pcp_car_link, headers=self.headers)
                yield Request(url, callback=self.parse_pcp_car_link, headers=self.headers, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com:80"})
            else:
                # yield Request(url, callback=self.parse_ch_car_link, headers=self.headers)
                yield Request(url, callback=self.parse_ch_car_link, headers=self.headers, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com:80"})

    def parse_pcp_car_link(self, response):
        """
        Function for parse url PCP
        """

        
        links = self.getTexts(response, '//a[@class="audi-button audi-button--ghost nm-mediatext-combination-fullwidth-textblock-link nm-layerLink"]/@href')
        for link in links:
            url = response.urljoin(link)
            # print("url", response.url)
            # print("url", url)
            # input("jkf")

        #     yield Request(url, callback=self.parse_json_date_in_table, headers=self.headers})
            yield Request(url, callback=self.parse_json_date_in_table, headers=self.headers, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com:80"})

    def parse_json_date_in_table(self, response):
        """
        Function for parse Full data for One item
        """
       

        modelName = self.getTextAll(response,'//div[@data-module="text-html"]/text()')
        if "representative example for" in modelName:
            carModel = modelName.split("representative example for")[1].split("subject to a")[0]
        elif "epresentative example for" in modelName:
            carModel = modelName.split("epresentative example for")[1].split("subject to a")[0]
        else:
            carModel = str()  

        carImageURL = urljoin(response.url, self.getText(response,'//picture//source/@data-srcset'))


        mon_payment = self.getText(response,'//table/tbody/tr/td[contains(text(), "44 monthly payments of") or contains(text(), "47 monthly payments of") or contains(text(), "23 monthly payments") or contains(text(), "monthly payments")]/following-sibling::td/text()')
        MonthlyPayment = self.remove_gbp(mon_payment.replace(",", "")).strip("\\r\\n")

        customer_deposit = self.getText(response,'//table/tbody/tr/td[contains(text(), "Customer deposit")]/following-sibling::td/text()')
        CustomerDeposit = self.remove_gbp(customer_deposit.replace(",", "")).strip("\\r\\n")

        deposit_contribution = self.getText(response,'//table/tbody/tr/td[contains(text(), "Centre Deposit Contribution") or contains(text(), "Audi Contribution^")]/following-sibling::td/text()')
        totalDepositContribution = self.remove_gbp(deposit_contribution).strip("\\r\\n")
        # print("totalDepositContribution: ", totalDepositContribution)
        # input("stop")

        otr_price = self.getText(response,'//table/tbody/tr/td[contains(text(), "Recommended on-the-road price (inc metallic paint)") or contains(text(), "Recommended on-the-road price")]/following-sibling::td/text()')
        OnTheRoadPrice = self.remove_gbp(otr_price.replace(",", "")).strip("\\r\\n")

        opt_final_payment = self.getText(response,'//table/tbody/tr/td[contains(text(), "Optional final payment")]/following-sibling::td/text()')
        OptionalPurchase_FinalPayment = self.remove_gbp(opt_final_payment.replace(",", "")).strip("\\r\\n")


        amm_of_credit = self.getText(response,'//table/tbody/tr/td[contains(text(), "Amount of credit")]/following-sibling::td/text()')
        AmountofCredit = self.remove_gbp(amm_of_credit.replace(",", "")).strip("\\r\\n")

        amm_payable = self.getText(response,'//table/tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/text()')
        TotalAmountPayable = self.remove_gbp(amm_payable.replace(",", "")).strip("\\r\\n")

        opt_fee = self.getText(response,'//table/tbody/tr/td[contains(text(), "Option to purchase fee")]/following-sibling::td/text()')
        OptionToPurchase_PurchaseActivationFee = self.remove_gbp(opt_fee).strip("\\r\\n")

        rate_of_int = self.getText(response,'//table/tbody/tr/td[contains(text(), "Rate of Interest p.a.")]/following-sibling::td/text()')
        FixedInterestRate_RateofinterestPA = rate_of_int.split("%")[0].strip("\\r\\n")

        apr = self.getText(response,'//table/tbody/tr/td[contains(text(), "Representative APR")]/following-sibling::td/text()')
        RepresentativeAPR = apr.split('%')[0].strip("\\r\\n")

        excess_mil = self.getText(response,'//table/tbody/tr/td[contains(text(), "Excess mileage")]/following-sibling::td/text()')
        ExcessMilageCharge = excess_mil.split('p per mile')[0].strip("\\r\\n")

        duration = self.getText(response,'//table/tbody/tr/td[contains(text(), "Duration")]/following-sibling::td/text()')
        if "2" in duration:
            DurationofAgreement = '24'
        elif "3" in duration:
            DurationofAgreement = '36'
        elif "4" in duration:
            DurationofAgreement = '48'
        else:
            DurationofAgreement = '48'
        
        TypeofFinance = 'Personal Contract Plan'
        item = CarItem()
        item['CarMake'] = 'Audi'
        if "Audi" in carModel:
            carModels = carModel.split("Audi")[1].strip()
        else:
            carModels =  carModel
        item['CarModel'] = self.remove_special_char_on_excel(carModels)
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
        item['CustomerDeposit'] = float(CustomerDeposit)
        if totalDepositContribution:
            item['RetailerDepositContribution'] = self.make_two_digit_no(str(totalDepositContribution))
        else:
            item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = OnTheRoadPrice
        item['OptionalPurchase_FinalPayment'] =  OptionalPurchase_FinalPayment
        item['AmountofCredit'] =  AmountofCredit
        item['DurationofAgreement'] = DurationofAgreement
        item['TotalAmountPayable'] = TotalAmountPayable
        item['OptionToPurchase_PurchaseActivationFee'] = OptionToPurchase_PurchaseActivationFee
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
        item['FixedInterestRate_RateofinterestPA'] = FixedInterestRate_RateofinterestPA
        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] =  OnTheRoadPrice
        item['CarimageURL'] = carImageURL
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        yield item

    #### AUDI Contract Hire Car###
    def parse_ch_car_link(self, response):
        """
        Function for audi CH cars
        """
        links = self.getTexts(response, '//a[@class="audi-button audi-button--ghost nm-mediatext-combination-fullwidth-textblock-link nm-layerLink"]/@href')
        for link in links:
            url = response.urljoin(link)

            # yield Request(url, callback=self.parse_ch_car_items, headers=self.headers)
            yield Request(url, callback=self.parse_ch_car_items, headers=self.headers, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com:80"})

    def parse_ch_car_items(self, response):
        """
        Function for parse items CH
        """

        modelName = self.getTextAll(response,'//div[@data-module="text-html"]/text()')

        # if "10,000 miles" in modelName:
        audiModel = modelName.split("10,000")[0].split(". ")[-1].strip()
        # else:
        #     audiModel = modelName
        # print("audiModel: ",audiModel)
        # print("res",response.url)
        # input("wait")
  
        carImageURL = urljoin(response.url, self.getText(response,'//picture//source/@data-srcset'))


        mon_payment = self.getText(response,'//table/tbody/tr/td[div[contains(text(), "monthly rentals of")]]/following-sibling::td/div/text()')
        # MonthlyPayment = self.remove_gbp(mon_payment.replace(",", "")).strip("\\r\\n")
        MonthlyPayment = "".join(re.findall("\d+|\.\d+", mon_payment))
        if MonthlyPayment!="":
            MonthlyPayment = float(MonthlyPayment)
            Monthly_Payment = "{:.2f}".format(MonthlyPayment)
        else:
            Monthly_Payment = ""

        customer_deposit = self.getText(response,'//table/tbody/tr/td[div[contains(text(), "Initial rental")]]/following-sibling::td/div/text()')
        CustomerDeposit = self.remove_gbp(customer_deposit.replace(",", "")).strip("\\r\\n")

        ExcessMilageCharge = self.getText(response,'//table/tbody/tr/td[div[contains(text(), "Excess mileage")]]/following-sibling::td/div/text()')
        ExcessMilageCharge = self.remove_gbp(ExcessMilageCharge.replace(",", "")).strip("\\r\\n")
        

        typeOfFinance = 'Business Contract Hire'
        item = CarItem()
        item['CarMake'] = 'Audi'
        item['CarModel'] = self.remove_special_char_on_excel(audiModel)
        item['TypeofFinance'] = self.get_type_of_finance(typeOfFinance)
        # item['MonthlyPayment'] = float(MonthlyPayment)
        item['MonthlyPayment'] = Monthly_Payment
        item['OnTheRoadPrice'] = 'N/A'
        item['DurationofAgreement'] = '36'
        item['CustomerDeposit'] = CustomerDeposit
        if not item['CustomerDeposit']:
            item['CustomerDeposit'] = 'N/A'
        item['AmountofCredit'] =  'N/A'
        item['TotalAmountPayable'] = 'N/A'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = 'N/A'
        item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        item['OfferExpiryDate'] = '03/06/2022'
        item['OptionalPurchase_FinalPayment'] = 'N/A'
        item['RetailerDepositContribution'] = 'N/A'
        if ExcessMilageCharge:
            item['ExcessMilageCharge'] = self.remove_percentage_sign(str(ExcessMilageCharge))
        else:
            item['ExcessMilageCharge'] = 'N/A'
        item['AverageMilesPerYear'] = '10000'
        item['RetailCashPrice'] =  'N/A'
        item['CarimageURL'] = carImageURL
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = response.url
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        yield item
