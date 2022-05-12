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



def get_filtered_list(string_to_filter, list_of_lists, optional_string =""):
    filtered_lists = [i for i in list_of_lists if string_to_filter in i]
    if len(filtered_lists) > 0:
        filtered_list = filtered_lists[0]
        return filtered_list
    else:
        return False

def flatten(l, a):
    for i in l:
        if isinstance(i, list):
            flatten(i, a)
        else:
            a.append(i)
    return a


class MazdaCar(BaseSpider):
    name = "mazda_co_uk"
    allowed_domains = []
    holder = list()
    start_url = ['https://www.mazda.co.uk/offers/retail-offers/', 'https://www.mazda.co.uk/offers/business-offers/', 'https://www.mazda.co.uk/offers/personal-contract-hire-leasing/', 'https://www.mazda.co.uk/offers/mazda-mx-30-offer/']
    # start_url = ['https://www.mazda.co.uk/offers/business-offers/','https://www.mazda.co.uk/offers/personal-contract-hire-leasing/']
    base_url = 'https://www.mazda.co.uk/'

    def __init__(self):
        super(MazdaCar, self).__init__()
        self.i = 0

    def start_requests(self):
        """ Start request
        """
        for url in self.start_url:
            if "retail-offers" in url: ### PCP & HP
                yield Request(url, callback=self.parse_for_offers_link, headers=self.headers)
            elif "business-offers" in url: ### business-offers
                yield Request(url, callback=self.parse_for__business_offers_link, headers=self.headers)
            elif "mazda-mx-30-offer" in url:
                img = ''
                yield Request(url, callback=self.parse_offers_data, headers=self.headers, dont_filter=True, meta={"image":img})
            else: ### personal-contract-hire
                yield Request(url, callback=self.parse_for__personal_contract_hire_link, headers=self.headers)

    def parse_for_offers_link(self, response):
        """ PCP OFFERS
        """
        scriptLoop = self.getTexts(response, '//script[contains(text(), "offersListingItem")]/text()')
        for data in scriptLoop:
            data = data.split("push(JSON.parse('")[1].split("'))")[0]
            jsonData = json.loads(data)
            # print("jsonData: ", jsonData)
            # input("wait here")
            body = jsonData['props']['ctas']['body']
            image = jsonData['props']['image']['url']
            for financeTypeOffers in body:
                link = urljoin(response.url, financeTypeOffers['link'])
                yield Request(link, callback=self.parse_offers_data, headers=self.headers, meta={"image":image})

        #################### BUSINESS Contract Hire  #####################
    def parse_for__business_offers_link(self, response):
        """ CH OFFERS
        """
        scriptLoop = self.getTexts(response, '//script[contains(text(), "offersListingItem")]/text()')
        for data in scriptLoop:
            data = data.split("push(JSON.parse('")[1].split("'))")[0]
            jsonData = json.loads(data)
            #################
            title = jsonData['props']['title']
            regex = r"[\$|€|£\20AC\00A3]{1}\d+\.?\d{0,2}"
            MonthlyPayment = re.search(regex, title).group()
            #################
            subTitle = jsonData['props']['subTitle']
            regex = r"[\$|€|£\20AC\00A3]{1}\d+(?:,\d+){0,2}"
            CustomerDeposit = re.search(regex, subTitle).group()
            #################
            CarModel = subTitle.split("br>")[1]
            #################

            description = jsonData['props']['description']
            CarimageURL = jsonData['props']['image']['url']
            my_str = description.replace("\\", "")
            data =  my_str.replace('u003c', '<')
            data =  data.replace('u003e', '>')

            selector = Selector(text=data, type="html")
            DurationofAgreement = selector.xpath('//ul/li[contains(text(), "Duration")]/text()').extract_first()
            AnnualMileage = selector.xpath('//ul/li[contains(text(), "Miles Per")]/text()').extract_first()

            # print("datas: ", selector)
            # print("matches: ", AnnualMileage)
            # input("wait here")

            item = CarItem()
            item['CarMake'] = 'Mazda'
            if "00D" in CarModel:
                item['CarModel'] = self.remove_special_char_on_excel(CarModel.split("00D")[1])
            else:
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = self.get_type_of_finance("CH")
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
            item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = self.remove_percentage_sign(self.reText(DurationofAgreement, r'([\d\.\,]+)'))
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = self.remove_percentage_sign(self.reText(AnnualMileage, r'([\d\.\,]+)'))
            item['OfferExpiryDate'] = "30/06/2022"
            item['RetailCashPrice'] = 'N/A'
            item['CarimageURL'] = CarimageURL
            item['WebpageURL'] = response.url
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            yield item

            #################### Personal Contract Hire  #####################

    def parse_for__personal_contract_hire_link(self, response):
        """ PERSONAL CONTRACT HIRE OFFERS
        """
        scriptLoop = self.getTexts(response, '//script[contains(text(), "offersListingItem")]/text()')
        for data in scriptLoop:
            data = data.split("push(JSON.parse('")[1].split("'))")[0]
            jsonData = json.loads(data)
            #################
            title = jsonData['props']['title']
            regex = r"[\$|€|£\20AC\00A3]{1}\d+\.?\d{0,2}"
            MonthlyPayment = re.search(regex, title).group()
            #################
            subTitle = jsonData['props']['subTitle']
            regex = r"[\$|€|£\20AC\00A3]{1}\d+(?:,\d+){0,2}"
            CustomerDeposit = re.search(regex, subTitle).group()
            #################
            CarModel = subTitle.split("br>")[1]
            #################

            description = jsonData['props']['description']
            CarimageURL = jsonData['props']['image']['url']
            my_str = description.replace("\\", "")
            data =  my_str.replace('u003c', '<')
            data =  data.replace('u003e', '>')

            selector = Selector(text=data, type="html")
            DurationofAgreement = selector.xpath('//ul/li[contains(text(), "Duration")]/text()').extract_first()
            AnnualMileage = selector.xpath('//ul/li[contains(text(), "Miles Per")]/text()').extract_first()

            # print("datas: ", selector)
            # print("matches: ", AnnualMileage)
            # input("wait here")

            item = CarItem()
            item['CarMake'] = 'Mazda'
            if "00D" in CarModel:
                item['CarModel'] = self.remove_special_char_on_excel(CarModel.split("00D")[1])
            else:
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = self.get_type_of_finance("Personal Contract Hire")
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
            item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = self.remove_percentage_sign(self.reText(DurationofAgreement, r'([\d\.\,]+)'))
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = self.remove_percentage_sign(self.reText(AnnualMileage, r'([\d\.\,]+)'))
            item['OfferExpiryDate'] = "30/06/2022"
            item['RetailCashPrice'] = 'N/A'
            item['CarimageURL'] = CarimageURL
            item['WebpageURL'] = response.url
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            yield item

        #################### PCP  #####################

    def parse_offers_data(self, response):
        """ PCP OFFERS here
        """

        CarimageURL = response.meta['image']
        scriptLoop = self.getTexts(response, '//script[contains(text(), "gradeOfferTable")]/text()')
        if not scriptLoop:
            scriptLoop = self.getTexts(response, '//script[contains(text(), "All-new Mazda MX-30 145ps First Edition Auto")]/text()')


        for data in scriptLoop:
            data = data.split("push(JSON.parse('")[1].split("'))")[0]
            jsonData = json.loads(data)

            # print("models: ", jsonData)
            # input("wait here:")
            if "mazda-mx-30-offer" in response.url:
                props = jsonData['submodules'][0]['props']
                modelsData = props['rows']

                Monthly_Payment_list = get_filtered_list("Monthly Payment", modelsData)
                if not Monthly_Payment_list:
                    Monthly_Payment_list = get_filtered_list("Followed by Consecutive Monthly Payments of", modelsData)
                APR_list = get_filtered_list("% APR", modelsData)
                OTR_list = get_filtered_list("On The Road Price inc Metallic Paint", modelsData)


                # CompanyDeposit_list =  get_filtered_list("Mazda Deposit Contribution", modelsData)
                CustomerDeposit_list = get_filtered_list("Customer Deposit", modelsData)
                AmountOfCredit_list = get_filtered_list("Amount of Credit", modelsData)
                OptionalFinalPayment_list = get_filtered_list("Optional Final Payment", modelsData)
                TotalAmountPayable_list = get_filtered_list("Total Amount Payable", modelsData)
                RateOfInterest_list = get_filtered_list("Fixed Rate of Interest", modelsData)
                Duration_list = get_filtered_list("No of monthly payments", modelsData)
                AnnualMileage_list = get_filtered_list("Annual Mileage", modelsData)
                ExcessMileageCharge_list = get_filtered_list("Excess Mileage Charge per mile", modelsData)
                if Monthly_Payment_list != False:
                    for i,monthly_payment in enumerate(Monthly_Payment_list):
                        if i == 0:
                            continue
                        Monthly_Payment = monthly_payment
                        APR = APR_list[i]
                        OTR = OTR_list[i]
                        # CompanyDeposit = CompanyDeposit_list[i]
                        CustomerDeposit = CustomerDeposit_list[i]
                        AmountOfCredit = AmountOfCredit_list[i]
                        OptionalFinalPayment = OptionalFinalPayment_list[i]
                        TotalAmountPayable = TotalAmountPayable_list[i]
                        RateOfInterest = RateOfInterest_list[i]
                        Duration = Duration_list[i]
                        AnnualMileage = AnnualMileage_list[i]
                        ExcessMileageCharge = ExcessMileageCharge_list[i]

                        item = CarItem()
                        item['CarMake'] = 'Mazda'
                        # item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                        item['CarModel'] = 'All-new Mazda MX-30 145ps First Edition Auto'
                        item['TypeofFinance'] = self.get_type_of_finance("PCP")
                        item['MonthlyPayment'] = self.make_two_digit_no(Monthly_Payment)
                        item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                        item['RetailerDepositContribution'] = 'N/A'
                        item['OnTheRoadPrice'] = self.remove_gbp(OTR)
                        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalFinalPayment)
                        item['AmountofCredit'] = self.remove_gbp(AmountOfCredit)
                        item['DurationofAgreement'] = Duration
                        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
                        item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
                        item['RepresentativeAPR'] = self.remove_percentage_sign(APR)
                        item['FixedInterestRate_RateofinterestPA'] = RateOfInterest.split("%")[0]
                        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMileageCharge)
                        item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage)
                        item['OfferExpiryDate'] = "30/06/2022"
                        item['RetailCashPrice'] = self.remove_gbp(OTR)
                        item['CarimageURL'] = CarimageURL
                        item['WebpageURL'] = response.url
                        item['DebugMode'] = self.Debug_Mode
                        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                        try:
                            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                        except:
                            item['DepositPercent'] = float()
                        yield item


            elif "-pcp-offers" in response.url or "/mazda6-tourer-offers-pcp" in response.url:
                grades = jsonData['props']['grades'] ### Multiple Model name loop
                for models in grades:
                    # if "mx-30" in response.url:
                    #     print("models: ", response.url)
                    #     print("scriptLoop: ", models)
                    #     input("wait here:")
                    # print("models: ", models)
                    # input("wait here:")
                    CarModel = models['grade']
                    modelsData = models['rows']

                    Monthly_Payment_list = get_filtered_list("Monthly Payment", modelsData)
                    if not Monthly_Payment_list:
                        Monthly_Payment_list = get_filtered_list("Followed by Consecutive Monthly Payments of", modelsData)
                    APR_list = get_filtered_list("% APR", modelsData)
                    OTR_list = get_filtered_list("On The Road Price inc Metallic Paint", modelsData)

                    CompanyDeposit_list =  get_filtered_list("Mazda Deposit Contribution", modelsData)
                    CustomerDeposit_list = get_filtered_list("Customer Deposit", modelsData)
                    AmountOfCredit_list = get_filtered_list("Amount of Credit", modelsData)
                    OptionalFinalPayment_list = get_filtered_list("Optional Final Payment", modelsData)
                    TotalAmountPayable_list = get_filtered_list("Total Amount Payable", modelsData)
                    RateOfInterest_list = get_filtered_list("Fixed Rate of Interest", modelsData)
                    Duration_list = get_filtered_list("No of monthly payments", modelsData)
                    AnnualMileage_list = get_filtered_list("Annual Mileage", modelsData)
                    ExcessMileageCharge_list = get_filtered_list("Excess Mileage Charge per mile", modelsData)

                    for i,monthly_payment in enumerate(Monthly_Payment_list):
                        if i == 0:
                            continue
                        Monthly_Payment = monthly_payment
                        APR = APR_list[i]
                        OTR = OTR_list[i]
                        CompanyDeposit = CompanyDeposit_list[i]
                        CustomerDeposit = CustomerDeposit_list[i]
                        AmountOfCredit = AmountOfCredit_list[i]
                        OptionalFinalPayment = OptionalFinalPayment_list[i]
                        TotalAmountPayable = TotalAmountPayable_list[i]
                        RateOfInterest = RateOfInterest_list[i]
                        Duration = Duration_list[i]
                        AnnualMileage = AnnualMileage_list[i]
                        ExcessMileageCharge = ExcessMileageCharge_list[i]


                        if "-conditional-sale" in response.url or "-conditional-offer" in response.url:
                            TypeofFinance = 'HP'
                        else:
                            TypeofFinance = 'PCP' 

                        item = CarItem()
                        item['CarMake'] = 'Mazda'
                        item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
                        item['MonthlyPayment'] = self.make_two_digit_no(Monthly_Payment)
                        item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                        item['RetailerDepositContribution'] = self.remove_gbp(CompanyDeposit)
                        item['OnTheRoadPrice'] = self.remove_gbp(OTR)
                        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalFinalPayment)
                        item['AmountofCredit'] = self.remove_gbp(AmountOfCredit)
                        item['DurationofAgreement'] = Duration
                        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
                        item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
                        item['RepresentativeAPR'] = self.remove_percentage_sign(APR)
                        item['FixedInterestRate_RateofinterestPA'] = RateOfInterest.split("%")[0]
                        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMileageCharge)
                        item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage)
                        item['OfferExpiryDate'] = "30/06/2022"
                        item['RetailCashPrice'] = self.remove_gbp(OTR)
                        item['CarimageURL'] = CarimageURL
                        item['WebpageURL'] = response.url
                        item['DebugMode'] = self.Debug_Mode
                        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                        try:
                            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                        except:
                            item['DepositPercent'] = float()
                        yield item

            else:
                grades = jsonData['props']['grades'] ### Multiple Model name loop
                for models in grades:
                    # print("models: ", models)
                    # input("wait here:")
                    CarModel = models['grade']
                    modelsDataHP = models['rows']
                    myDictionary = dict()
                    for i, data in enumerate(modelsDataHP):
                        if i == 0:
                            continue
                        key = data[0]
                        value = data[1]
                        myDictionary.update({key:value})


                    # if "mazda6-tourer-offers-pcp/" in response.url:
                    #     print("duration", myDictionary)
                    #     input("sto")

                    # print("keys: ", key)
                    # print("OnTheRoadPrice: ", OnTheRoadPrice)
                    # print("myDictionary:", myDictionary)
                    # print("res:", response.url)
                    # input("wait here:")

                    if "36 Monthly Payments of" in myDictionary:
                        MonthlyPayment = myDictionary['36 Monthly Payments of']
                    elif "Monthly Payment" in myDictionary:
                        MonthlyPayment = myDictionary['Monthly Payment']

                    if "On The Road Price  inc Metallic Paint" in myDictionary:
                        OnTheRoadPrice = myDictionary['On The Road Price  inc Metallic Paint']
                    elif "On The Road Price inc Metallic Paint" in myDictionary:
                        OnTheRoadPrice = myDictionary['On The Road Price inc Metallic Paint']

                    CustomerDeposit = myDictionary['Customer Deposit']
                    AmountofCredit = myDictionary['Amount of Credit']
                    TotalAmountPayable = myDictionary['Total Amount Payable']
                    FixedInterestRate_RateofinterestPA = myDictionary['Fixed Rate of Interest']
                    if "Representative APR" in myDictionary:
                        RepresentativeAPR = myDictionary['Representative APR']
                    elif "APR" in myDictionary:
                        RepresentativeAPR = myDictionary['APR']
                    elif "% APR" in myDictionary:
                        RepresentativeAPR = myDictionary['% APR']

                    duration = myDictionary['Duration of Agreement']
                    

                    if "3" in duration:
                        DurationofAgreement = '36'
                    elif "4" in duration:
                        DurationofAgreement = "48"
                    elif "2" in duration:
                        DurationofAgreement = "24"
                    
                    if "-conditional-sale" in response.url or "-conditional-offer" in response.url:
                        TypeofFinance = 'HP'
                    else:
                        TypeofFinance = 'PCP'    


                    item = CarItem()
                    item['CarMake'] = 'Mazda'
                    item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                    item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
                    item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                    item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                    item['RetailerDepositContribution'] = 'N/A'
                    item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
                    item['OptionalPurchase_FinalPayment'] = 'N/A'
                    item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                    item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
                    item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                    item['FixedInterestRate_RateofinterestPA'] = FixedInterestRate_RateofinterestPA.split("%")[0]
                    item['ExcessMilageCharge'] = 'N/A'
                    item['AverageMilesPerYear'] = 'N/A'
                    item['OfferExpiryDate'] = "30/06/2022"
                    item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
                    item['CarimageURL'] = CarimageURL
                    item['WebpageURL'] = response.url
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    try:
                        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    except:
                        item['DepositPercent'] = float()
                    yield item
