# -*- coding: utf-8 -*-
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
from scrapy.selector import Selector
import math

###############PCP AND Contract HIRE BOTH###########################
###############PCP AND Contract HIRE BOTH###########################

class MitsubishiSpider(BaseSpider):
    name = "mitsubishi.co.uk"

    # handle_httpstatus_list = [404]

    allowed_domains = ['mitsubishi-cars.co.uk']
    start_url = ["https://finance.mitsubishi-motors.co.uk/getVariantsByModel/", "https://www.mitsubishi-motors.co.uk/buy/offers/business/l200"]
    base_url  = 'https://www.mitsubishi-cars.co.uk'
    def __init__(self):
        super(MitsubishiSpider, self).__init__()

    # def start_requests(self):

    # def start_requests(self):
    #     formdata = {"modelCode":"L200%"}
    #     yield FormRequest(self.start_url, callback=self.parse_model_varients, formdata=formdata, headers=self.headers)

    def start_requests(self):
        for url in self.start_url:
            if "getVariantsByModel/" in url:
                formdata = {"modelCode":"L200%"}
                yield FormRequest(url, callback=self.parse_model_varients, formdata=formdata, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_car_link, headers=self.headers)
    #######################################################
    #################### CONTRACT HIRE  ###################
    ######################################################

    def parse_car_link(self, response):
        """ Function for parse Links
        """
        carpath = response.xpath('//div[@class="theme-default-with-icons__col-xs-12___3BYpq theme-default-with-icons__col-sm-4___2jBkz medium__columnWrapper___22VyI"]')
        for car in carpath:
            CarModel = self.getText(car, './/h2/text()')
            CarimageURL = self.getText(car, './/img[@class="medium__image___s2EF-"]/text()')
            MonthlyPayment = self.getText(car, './/p[@class="theme-default-with-icons__marginBottom20___3uimw theme-default-with-icons__headingSix___mqgSJ"]/text()')
            CustomerDeposit = self.getText(car, './/p[@class="theme-default-with-icons__marginBottom20___3uimw theme-default-with-icons__headingSix___mqgSJ"]/text()').split("plus £")[1].split("initial")[0]

            data_text = self.getText(response, '//div[@class="common-rich-text__richText___2kyWa theme-default-with-icons__smallType___aTjXq "]//p[2]/text()')
            excess_milleage = data_text.split("p + VAT per mile")


            # print("url:", response.url)
            # print("data_text:", excess_milleage)
            # # print("mill:", excess_milleage)
            # # # # print("MonthlyPayment:",MonthlyPayment)
            # # # # print("ExcessMilageCharge:",ExcessMilageCharge)
            # # # # print("DurationofAgreement:",DurationofAgreement)
            # input("stop")

            carMake = 'Mitsubishi'
            item = CarItem()
            item['CarMake'] = carMake
            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = 'Commercial Contract Hire'
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
            item['RetailerDepositContribution'] = 'N/A'
            item['AmountofCredit'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['DurationofAgreement'] = '36'
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            if "Warrior " in CarModel:
                item['ExcessMilageCharge'] = excess_milleage[0].split("excess mileage @")[1]
            elif "Barbarian Manual" in CarModel:
                item['ExcessMilageCharge'] = excess_milleage[1].split("excess mileage @")[1]
            else:
                item['ExcessMilageCharge'] = excess_milleage[2].split("excess mileage @")[1]
            item['AverageMilesPerYear'] = '8000'
            item['OfferExpiryDate'] = '31/07/2021'
            item['RetailCashPrice'] = 'N/A'
            item['WebpageURL'] = response.url
            item['CarimageURL'] = CarimageURL
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            # yield item



            #######################################################
            ###################### PCP  and HP ###########################
            ######################################################

    def parse_model_varients(self, response):
        JO = json.loads(response.body)
        for cars in JO:

            Variant = cars['Variant']
            TrimStyle = cars['TrimStyle']
            altDescription = cars['altDescription']
            otr = cars['otr']
            Varient_name = TrimStyle+" "+altDescription
            formdata = {"variantCode":Variant}
            url = "https://finance.mitsubishi-motors.co.uk/getVariantData/"
            TypeofFinance = ['HP','PCP']
            for types in TypeofFinance:
                if 'HP' in types:
                    function = self.parse_model_hp
                else:
                    function = self.parse_model_pcp
                yield FormRequest(url, callback=function, formdata=formdata,dont_filter=True, headers=self.headers, meta={
                        'Varient_name': Varient_name,
                    })


    def parse_model_hp(self, response):
        Varient_name = response.meta.get('Varient_name')
        jO = json.loads(response.body)
        # print("url", response.url)
        # print("jO", jO)
        # input("stop")
        months = [12,24,36,42]
        CustomerDeposit = 5000
        for term in months:
            variend_id = jO['otr']['Variant']
            car_url = "https://finance.mitsubishi-motors.co.uk/calculator/l200/"+str(variend_id)+"/"+str(term)+"/6000/"+str(CustomerDeposit)+"/0"
            tempTerm = 48 if term == 42 else term
            aprHP = float(jO['hp']['rate'+str(tempTerm)])
            # tempaprHP = jO['hp']['purchaseFee'] if aprHP == 0 else aprHP
            # cffa = jO['hp']['cffa']
            cffa = 0
            OTR = jO['hp']['OTR']
            purchaseFee = jO['hp']['purchaseFee']
            loanHP = OTR - CustomerDeposit
            advance = float(loanHP + cffa)
            charges = (advance*aprHP*term)/1200
            MonthlyPaymentHP = round((((advance + charges)*100)/term)/100, 2)
            # roundedMonthlyPaymentHP = round((((advance + charges - cffa) * 100) / (term - 1)) / 100);
            TotalAmountPayableHP = round((MonthlyPaymentHP*term)+CustomerDeposit)
            APR = "6.2%" if term == 42 else "0%"

            item = CarItem()
            item['CarMake'] = 'Mitsubishi'
            item['CarModel'] = self.remove_special_char_on_excel('L200'+Varient_name)
            item['TypeofFinance'] = self.get_type_of_finance('Hire Purchase')
            item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPaymentHP))
            item['CustomerDeposit'] = self.make_two_digit_no(str(CustomerDeposit))
            item['RetailerDepositContribution'] = 0
            item['OnTheRoadPrice'] = OTR
            item['OptionalPurchase_FinalPayment'] = MonthlyPaymentHP
            item['AmountofCredit'] = loanHP
            item['DurationofAgreement'] = term
            item['TotalAmountPayable'] = TotalAmountPayableHP
            item['OptionToPurchase_PurchaseActivationFee'] = self.remove_percentage_sign(str(purchaseFee))
            item['RepresentativeAPR'] = self.remove_percentage_sign(APR)
            item['FixedInterestRate_RateofinterestPA'] = "N/A"
            item['ExcessMilageCharge'] = "N/A"
            item['AverageMilesPerYear'] = 'Unlimited'
            item['OfferExpiryDate'] = '31/12/2021'
            # item['OfferExpiryDate'] = 'N/A'
            item['RetailCashPrice'] = OTR
            item['CarimageURL'] = ""
            item['WebpageURL'] = car_url
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            # if item['MonthlyPayment'] != '':
                # yield item


    def parse_model_pcp(self, response):
        Varient_name = response.meta.get('Varient_name')
        jO = json.loads(response.body)
        months = [24,36,42]
        CustomerDeposit = 5000
        contributionPCP = 2000
        PCP_FEE = 10
        miless = [6000, 10000, 12000, 18000, 24000]
        for miles in miless:
            for term in months:
                tempTerm = term+1
                variend_id = jO['otr']['Variant']
                gfv = jO['pcp']['gfv']["rv_" + str(tempTerm) + "_" + str(miles)]
                car_url = "https://finance.mitsubishi-motors.co.uk/calculator/l200/"+str(variend_id)+"/"+str(term)+"/"+str(miles)+"/"+str(CustomerDeposit)+"/0"
                OTR = jO['otr']['OTR']
                loanPCP = OTR - CustomerDeposit - contributionPCP
                APR = 5.9
                aprPCP = APR * 0.01
                rate = math.pow(1 + aprPCP, 1 / 12) - 1
                pv = -loanPCP + (float(gfv + PCP_FEE) / math.pow(1 + math.pow(1 + aprPCP, 1 / 12) - 1, tempTerm))
                q = math.pow(1 + rate, term);
                future_value = 0
                type = 0
                MonthlyPayment = round(-(rate * (future_value + (q * pv))) / ((-1 + q) * (1 + rate * (type))), 2)
                totalPayablePCP = (MonthlyPayment * (tempTerm - 1)) + float(gfv) + PCP_FEE + CustomerDeposit + contributionPCP
                OptionalPurchase_FinalPayment = gfv+ PCP_FEE


                item = CarItem()
                item['CarMake'] = 'Mitsubishi'
                item['CarModel'] = self.remove_special_char_on_excel('L200 '+Varient_name)
                item['TypeofFinance'] = self.get_type_of_finance('PCP')
                item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
                item['CustomerDeposit'] = self.make_two_digit_no(str(CustomerDeposit))
                item['RetailerDepositContribution'] = contributionPCP
                item['OnTheRoadPrice'] = OTR
                item['OptionalPurchase_FinalPayment'] = OptionalPurchase_FinalPayment
                item['AmountofCredit'] = loanPCP
                item['DurationofAgreement'] = term
                item['TotalAmountPayable'] = round(totalPayablePCP, 2)
                item['OptionToPurchase_PurchaseActivationFee'] = self.remove_percentage_sign(str(PCP_FEE))
                item['RepresentativeAPR'] = self.remove_percentage_sign(str(APR))
                item['FixedInterestRate_RateofinterestPA'] = "N/A"
                item['ExcessMilageCharge'] = jO['pcp']['gfv']['ppm']
                item['AverageMilesPerYear'] = self.remove_percentage_sign(str(miles))
                item['OfferExpiryDate'] = '31/12/2021'
                # item['OfferExpiryDate'] = 'N/A'
                item['RetailCashPrice'] = OTR
                item['CarimageURL'] = ""
                item['WebpageURL'] = car_url
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                # if item['MonthlyPayment'] != '':
                #     yield item
