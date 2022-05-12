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




class HondaSpider(BaseSpider):
    name = "honda.co.uk"
    allowed_domains = []
    holder = list()
    start_url = ['https://www.honda.co.uk/cars/offers.html',  'https://www.honda.co.uk/cars/new/corporate-services/contract-hire.html']
    # start_url = ['https://www.honda.co.uk/cars/offers.html']
        # start_url = ['http://www.honda.co.uk/cars.html', 'http://www.honda.co.uk/cars/new/corporate-services/contract-hire/jcr:content/contractHire.data.JSON']
    base_url = 'http://www.honda.co.uk'

    def __init__(self):
        super(HondaSpider, self).__init__()
        self.i = 0
        self.XPATH_CATEGORY_LEVEL_1 = '//div[@class="financialOfferCtas"]/div/a[@class="analyticsEvent primaryCta primaryCtaFull"]/@href'
        self.XPATH_CATEGORY_LEVEL_VANS = '//div[@class="vehicle-link"]//div[@class="starting-price"]//ul[@class="prices"]/li/div[@class="subtext"]/a/@href'


    def start_requests(self):
        """ Start request for Cars
        """
        for url in self.start_url:
            
            if "corporate-services" in url:
                yield Request(url, callback=self.parse_bch_offers_link, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_item_list, headers=self.headers)


    def parse_bch_offers_link(self, response):
        """ Function for BCH OFFERS
        """
        url = 'https://www.honda.co.uk/cars/new/corporate-services/contract-hire/jcr:content/contractHire.data.JSON'
        yield Request(url, callback=self.parse_for_bch_data, headers=self.headers)

    def parse_for_bch_data(self, response):
        """ Function for BCH OFFERS DATA
        """
        jsondata = json.loads(response.body)
        values_models = jsondata['option']['values']
        for val_model in values_models: ### Main Loop For Model Full Data
            values = val_model['option']['values']
            for val in values:
                values = val['option']['values'][0]
                values_1 = values['option']['values']
                for ab in values_1:
                    values_2 = ab['option']['values']
                    for cd in values_2:
                        values_3 = cd['option']['values']
                        for ef in values_3:
                            values_4 = ef['option']['values']
                            for gh in values_4:
                                table = gh['option']['values'][0]['table']
                                data = dict()
                                for tbl in table:
                                    label = tbl['label']
                                    value = tbl['value']
                                    data.update({label:value})
                                carModel = data['car']
                                MonthlyPayment = data['monthlyRental']
                                CustomerDeposit = data['advRentalExVat']
                                DurationofAgreement = data['termOf']
                                AverageMilesPerYear = data['mileage']
                                ExcessMilageCharge = data['excessMileage']

                                TypeofFinance = 'BCH'
                                carMake = 'Honda'
                                item = CarItem()
                                item['CarMake'] = carMake
                                item['CarModel'] = self.remove_special_char_on_excel(carModel)
                                item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
                                item['MonthlyPayment'] = self.make_two_digit_no(self.reText(MonthlyPayment, r'([\d\.\,]+)'))
                                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                                item['RetailerDepositContribution'] = 'N/A'
                                item['OnTheRoadPrice'] = 'N/A'
                                item['AmountofCredit'] = 'N/A'
                                item['DurationofAgreement'] = DurationofAgreement.split("months")[0]
                                item['OptionalPurchase_FinalPayment'] = 'N/A'
                                item['TotalAmountPayable'] = 'N/A'
                                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                                item['RepresentativeAPR'] = 'N/A'
                                item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                                item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
                                item['OfferExpiryDate'] = '30/06/2022'
                                item['RetailCashPrice'] = 'N/A'
                                item['WebpageURL'] = 'https://www.honda.co.uk/cars/new/corporate-services/contract-hire.html'
                                item['CarimageURL'] = ''
                                item['DebugMode'] = self.Debug_Mode
                                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                                yield item


    def parse_item_list(self, response):
        """ Function for parse item list
        """
        # print("URL",response.url)
        # input("wait")
        car_urls = response.xpath('//div[@class="range"]//div[contains(@class, "product-grid")]/div/div')
        for href in car_urls:
            car_url = self.getText(href,'.//a/@href')
            completeurls = urljoin("http://www.honda.co.uk",car_url)
            # print("completeurls: ", completeurls)
            # input("wait here11:")
            yield Request(completeurls, callback=self.more_url, headers=self.headers)

    def more_url(self, response):
        # print("URL",response.url)
        # input("wait")
        car_urls = response.xpath('//div[@class="container"]//div[@class="content-right"]')
        for href in car_urls:
            car_url = self.getText(href,'.//a/@href')
            completeurls = urljoin(response.url,car_url)
            yield Request(completeurls, callback=self.parse_item, headers=self.headers)



    def parse_item(self, response):
        print("URLS: ", response.url)
        # input("wait here11:")
        url=response.url
        carimage = self.getText(response,'//div[@class="container"]/div/div/picture//img/@src')
        car_image = "http://www.honda.co.uk"+ carimage
        if car_image !="":
            car_image = car_image
        else:
            car_image = "N/A"

        car_name = self.getText(response,'//div[@class="content-left"]/h4[@class="listing-title"]//text()')
        if car_name !="":
            car_name = car_name
        else:
            car_name = "N/A"

        car_make = 'Honda'

        
        # if monthlypayment != "":
        #     monthly_payment = "".join(re.findall("\d+|\.\d+", monthlypayment))
        #     monthly_payment = float(monthly_payment)
        # else:
        #     monthly_payment = ""

        pcphp = self.getTexts(response,'//div[@class="tabs-line-animate"]/div/a/text()')
        
        for detail in pcphp:
            if "PCP" in detail:
                # print("pcphp",detail)
                # input("wait")
                TypeofFinance = "Personal Contract Purchase"
                for url_info in response.xpath('//div[contains(@class, "tab1List1 financeTable") or contains(@class, "tab1List2 financeTable")]/table[@class="tabular-module-data"]'):
                    
                    monthlypayments = self.getText(url_info,'.//tr/td[contains(text(), "Payments of")]/following-sibling::td/text()')
                    if monthlypayments !="":
                        monthlypayments = monthlypayments
                    else:
                        monthlypayments = "N/A"

                    # print("monthlypayments",monthlypayments)
                    # input("wait")    

                    customerdeposit = self.getText(url_info,'.//tr/td[contains(text(), "Deposit")]/following-sibling::td/text()')
                    if customerdeposit !="":
                        customerdeposit = customerdeposit
                    else:
                        customerdeposit = "N/A"
                    # if customerdeposit != "":
                    #     customer_deposit = "".join(re.findall("\d+|\.\d+", customerdeposit))
                    #     customer_deposit = float(customer_deposit)
                    # else:
                    #     customer_deposit = ""

                    on_the_road_price = self.getText(url_info,'.//tr/td[contains(text(), "OTR Price") or contains(text(), "On the Road (OTR) Price*")]/following-sibling::td/text()')
                    if on_the_road_price !="":
                        on_the_road_price = on_the_road_price
                    else:
                        on_the_road_price = "N/A"

                    durations = self.getText(url_info,'.//tr/td[contains(text(), "Duration")]/following-sibling::td/text()')
                    if durations !="":
                        durations = durations
                    else:
                        durations = "N/A"

                    amount_of_credit = self.getText(url_info,'.//tr/td[contains(text(), "Amount of Credit")]/following-sibling::td/text()')
                    if amount_of_credit !="":
                        amount_of_credit = amount_of_credit
                    else:
                        amount_of_credit = "N/A"

                    OptionalPurchase_FinalPayment = self.getText(url_info,'.//tr/td[contains(text(), "Final Payment inc Option Fee")]/following-sibling::td/text()')
                    if OptionalPurchase_FinalPayment !="":
                        OptionalPurchase_FinalPayment = OptionalPurchase_FinalPayment
                    else:
                        OptionalPurchase_FinalPayment = "N/A"

                    total_amount_payable = self.getText(url_info,'.//tr/td[contains(text(), "Total Amount Payable")]/following-sibling::td/text()')
                    if total_amount_payable !="":
                        total_amount_payable = total_amount_payable
                    else:
                        total_amount_payable = "N/A"

                    representative_apr = self.getText(url_info,'.//tr/td[contains(text(), "APR Representative")]/following-sibling::td/text()')
                    if representative_apr !="":
                        representative_apr = representative_apr
                    else:
                        representative_apr = "N/A"

                    average_miles_per_year = self.getText(url_info,'.//tr/td[contains(text(), "Annual Contracted Mileage")]/following-sibling::td/text()')
                    if average_miles_per_year !="":
                        average_miles_per_year = average_miles_per_year
                    else:
                        average_miles_per_year = "N/A"

                    excess_milage_charge = self.getText(url_info,'.//tr/td[contains(text(), "Excess Mileage Charge per mile")]/following-sibling::td/text()')
                    if excess_milage_charge !="":
                        excess_milage_charge = excess_milage_charge
                    else:
                        excess_milage_charge = "N/A"
                        # print("excess_milage_charge",excess_milage_charge)
                        # print("URL",response.url)
                        # input("wait")

                    FixedInterestRate_RateofinterestPA = self.getText(url_info,'.//tr/td[contains(text(), "Interest Rate Per Annum Fixed")]/following-sibling::td/text()')
                    if FixedInterestRate_RateofinterestPA !="":
                        FixedInterestRate_RateofinterestPA = FixedInterestRate_RateofinterestPA
                    else:
                        FixedInterestRate_RateofinterestPA = "N/A"

                    PurchaseActivationFee = self.getText(url_info,'.//tr/td[contains(text(), "Option to Purchase Fee")]/following-sibling::td/text()')
                    if PurchaseActivationFee !="":
                        PurchaseActivationFee = PurchaseActivationFee
                    else:
                        PurchaseActivationFee = "N/A"

                    OptionalPurchase_FinalPayment = self.getText(url_info,'.//tr/td[contains(text(), "Final Payment")]/following-sibling::td/text()')
                    if OptionalPurchase_FinalPayment !="":
                        OptionalPurchase_FinalPayment = OptionalPurchase_FinalPayment
                    else:
                        OptionalPurchase_FinalPayment = "N/A"



                    item = CarItem()
                    item['CarMake'] = car_make
                    item['CarModel'] = self.remove_special_char_on_excel(car_name)
                    item['TypeofFinance'] = TypeofFinance
                    item['MonthlyPayment'] = self.make_two_digit_no(self.reText(monthlypayments, r'([\d\.\,]+)'))
                    item['CustomerDeposit'] = self.make_two_digit_no(customerdeposit)
                    item['RetailerDepositContribution'] = 'N/A'
                    item['OnTheRoadPrice'] = self.remove_gbp(on_the_road_price)
                    item['AmountofCredit'] = self.remove_gbp(amount_of_credit)
                    item['DurationofAgreement'] = durations.split("months")[0]
                    item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
                    item['TotalAmountPayable'] = self.remove_gbp(total_amount_payable)
                    item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(PurchaseActivationFee)
                    item['RepresentativeAPR'] = self.remove_percentage_sign(representative_apr)
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                    item['ExcessMilageCharge'] = self.remove_percentage_sign(excess_milage_charge)
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(average_miles_per_year)
                    item['OfferExpiryDate'] = '30/06/2022'
                    item['RetailCashPrice'] = self.remove_gbp(on_the_road_price)
                    item['WebpageURL'] = response.url
                    item['CarimageURL'] = car_image
                    item['DebugMode'] = self.Debug_Mode
                    try:
                        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    except:
                        item['FinalPaymentPercent'] = float()
                    try:
                        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    except:
                        item['DepositPercent'] = float()
                    yield item

                    # print("customer_deposit",customer_deposit)

                    # print("customer_deposit",customer_deposit)
                    # print("durations",durations)
                    # print("amount_of_credit",amount_of_credit)
                    # print("OptionalPurchase_FinalPayment",OptionalPurchase_FinalPayment)
                    # print("total_amount_payable",total_amount_payable)

                    # print("representative_apr",representative_apr)
                    # print("average_miles_per_year",average_miles_per_year)
                    # print("representative_apr",excess_milage_charge)
                    # print("FixedInterestRate_RateofinterestPA",FixedInterestRate_RateofinterestPA)
                    # print("PurchaseActivationFee",PurchaseActivationFee)
                    # print("OptionalPurchase_FinalPayment",OptionalPurchase_FinalPayment)
                    # input("wait")

            if "HP" in detail:
                # print("hp: ",detail)
                # input("wait")
                TypeofFinance = "Hire Purchase"
                for url_infoHP in response.xpath('//div[contains(@class, "tab2List1 financeTable") or contains(@class, "tab2List2 financeTable")]/table[@class="tabular-module-data"]'):
                    
                    monthlypayment = self.getText(url_infoHP,'.//tr/td[contains(text(), "Payments of")]/following-sibling::td/text()')
                    if monthlypayment !="":
                        monthlypayment = monthlypayment
                    else:
                        monthlypayment = "N/A"

                    print("monthlypaymentsHP: ",monthlypayment)
                    # input("wait") 

                    customerdeposit = self.getText(url_infoHP,'.//tr/td[contains(text(), "Deposit")]/following-sibling::td/text()')
                    if customerdeposit !="":
                        customerdeposit = customerdeposit
                    else:
                        customerdeposit = "N/A"
                    # if customerdeposit != "":
                    #     customer_deposit = "".join(re.findall("\d+|\.\d+", customerdeposit))
                    #     customer_deposit = float(customer_deposit)
                    # else:
                    #     customer_deposit = ""

                    on_the_road_price = self.getText(url_infoHP,'.//tr/td[contains(text(), "OTR Price") or contains(text(), "On the Road (OTR) Price*")]/following-sibling::td/text()')
                    if on_the_road_price !="":
                        on_the_road_price = on_the_road_price
                    else:
                        on_the_road_price = "N/A"

                    durations = self.getText(url_infoHP,'.//tr/td[contains(text(), "Duration")]/following-sibling::td/text()')
                    if durations !="":
                        durations = durations
                    else:
                        durations = "N/A"

                    amount_of_credit = self.getText(url_infoHP,'.//tr/td[contains(text(), "Amount of Credit")]/following-sibling::td/text()')
                    if amount_of_credit !="":
                        amount_of_credit = amount_of_credit
                    else:
                        amount_of_credit = "N/A"

                    OptionalPurchase_FinalPayment = self.getText(url_infoHP,'.//tr/td[contains(text(), "Final Payment inc Option Fee")]/following-sibling::td/text()')
                    if OptionalPurchase_FinalPayment !="":
                        OptionalPurchase_FinalPayment = OptionalPurchase_FinalPayment
                    else:
                        OptionalPurchase_FinalPayment = "N/A"

                    total_amount_payable = self.getText(url_infoHP,'.//tr/td[contains(text(), "Total Amount Payable")]/following-sibling::td/text()')
                    if total_amount_payable !="":
                        total_amount_payable = total_amount_payable
                    else:
                        total_amount_payable = "N/A"

                    representative_apr = self.getText(url_infoHP,'.//tr/td[contains(text(), "APR Representative")]/following-sibling::td/text()')
                    if representative_apr !="":
                        representative_apr = representative_apr
                    else:
                        representative_apr = "N/A"

                    average_miles_per_year = self.getText(url_infoHP,'.//tr/td[contains(text(), "Annual Contracted Mileage")]/following-sibling::td/text()')
                    if average_miles_per_year !="":
                        average_miles_per_year = average_miles_per_year
                    else:
                        average_miles_per_year = "N/A"

                    excess_milage_charge = self.getText(url_infoHP,'.//tr/td[contains(text(), "Excess Mileage Charge per mile")]/following-sibling::td/text()')
                    if excess_milage_charge !="":
                        excess_milage_charge = excess_milage_charge
                    else:
                        excess_milage_charge = "N/A"

                    FixedInterestRate_RateofinterestPA = self.getText(url_infoHP,'.//tr/td[contains(text(), "Interest Rate Per Annum Fixed")]/following-sibling::td/text()')
                    if FixedInterestRate_RateofinterestPA !="":
                        FixedInterestRate_RateofinterestPA = FixedInterestRate_RateofinterestPA
                    else:
                        FixedInterestRate_RateofinterestPA = "N/A"

                    PurchaseActivationFee = self.getText(url_infoHP,'.//tr/td[contains(text(), "Option to Purchase Fee")]/following-sibling::td/text()')
                    if PurchaseActivationFee !="":
                        PurchaseActivationFee = PurchaseActivationFee
                    else:
                        PurchaseActivationFee = "N/A"

                    OptionalPurchase_FinalPayment = self.getText(url_infoHP,'.//tr/td[contains(text(), "Final Payment")]/following-sibling::td/text()')
                    if OptionalPurchase_FinalPayment !="":
                        OptionalPurchase_FinalPayment = OptionalPurchase_FinalPayment
                    else:
                        OptionalPurchase_FinalPayment = "N/A"

                    item = CarItem()
                    item['CarMake'] = car_make
                    item['CarModel'] = self.remove_special_char_on_excel(car_name)
                    item['TypeofFinance'] = TypeofFinance
                    item['MonthlyPayment'] = self.make_two_digit_no(self.reText(monthlypayment, r'([\d\.\,]+)'))
                    item['CustomerDeposit'] = self.make_two_digit_no(customerdeposit)
                    item['RetailerDepositContribution'] = 'N/A'
                    item['OnTheRoadPrice'] = self.remove_gbp(on_the_road_price)
                    item['AmountofCredit'] = self.remove_gbp(amount_of_credit)
                    item['DurationofAgreement'] = durations.split("months")[0]
                    item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
                    item['TotalAmountPayable'] = self.remove_gbp(total_amount_payable)
                    item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(PurchaseActivationFee)
                    item['RepresentativeAPR'] = self.remove_percentage_sign(representative_apr)
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                    # item['ExcessMilageCharge'] = self.remove_percentage_sign(excess_milage_charge)
                    item['ExcessMilageCharge'] = "N/A"
                    # item['AverageMilesPerYear'] = self.remove_percentage_sign(average_miles_per_year)
                    item['AverageMilesPerYear'] = "N/A"
                    item['OfferExpiryDate'] = '30/06/2022'
                    item['RetailCashPrice'] = self.remove_gbp(on_the_road_price)
                    item['WebpageURL'] = response.url
                    item['CarimageURL'] = car_image
                    item['DebugMode'] = self.Debug_Mode
                    try:
                        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    except:
                        item['FinalPaymentPercent'] = float()
                    try:
                        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    except:
                        item['DepositPercent'] = float()
                    yield item

                    # print("customer_deposit",customer_deposit)

                    # print("customer_deposit",customer_deposit)
                    # print("durations",durations)
                    # print("amount_of_credit",amount_of_credit)
                    # print("OptionalPurchase_FinalPayment",OptionalPurchase_FinalPayment)
                    # print("total_amount_payable",total_amount_payable)

                    # print("representative_apr",representative_apr)
                    # print("average_miles_per_year",average_miles_per_year)
                    # print("representative_apr",excess_milage_charge)
                    # print("FixedInterestRate_RateofinterestPA",FixedInterestRate_RateofinterestPA)
                    # print("PurchaseActivationFee",PurchaseActivationFee)
                    # print("OptionalPurchase_FinalPayment",OptionalPurchase_FinalPayment)
                    # input("wait")


    # def parse_item(self, response):
    #     """HONDA CAR ITEMS
    #     """
    #     car_image = self.getText(response, '//div[@class="imgWrapper"]/img/@src')

    #     carModel = self.getTexts(response, '//div[@class="wrapperInner"]//caption[@class="wrapperInner"]/text()')
    #     # print("car_url: ", carModel)
    #     # input("wait here11:")
    #     on_the_road_price = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "OTR Price")]/following-sibling::td/text()')

    #     customer_deposit = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr[@class="even"]/th[not(contains(text(),"Honda Deposit Contribution")) and contains(text(), "Deposit") or contains(text(), "Customer Deposit")]/following-sibling::td/text()')
    #     # if "20%" in customer_deposit:
    #     #     customer_deposit = ['5858.94']
    #     # elif "23%" in customer_deposit:
    #     #     customer_deposit = ['5887.37']
    #     monthly_payment = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Payments of") or contains(text(), "Monthly Payments")]/following-sibling::td/text()')

    #     durations = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Duration")]/following-sibling::td/text()')
    #     # if len(durations) > 1:
    #     #     duration = durations
    #     # else:
    #     #     duration = 'N/A'
    #     retailer_deposit_contribution = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Honda Deposit Contribution*") or contains(text(), "Honda Deposit Contribution†")]/following-sibling::td/text()')

    #     amount_of_credit = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Amount of Credit")]/following-sibling::td/text()')

    #     OptionalPurchase_FinalPayment = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Final Payment") and not(contains(text(), "Final Payment inc Option Fee"))]/following-sibling::td/text()')

    #     total_amount_payable = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Total Amount Payable")]/following-sibling::td/text()')

    #     representative_apr = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "APR Representative")]/following-sibling::td/text()')

    #     PurchaseActivationFee = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Option to Purchase Fee")]/following-sibling::td/text()')

    #     average_miles_per_year = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Annual Contracted Mileage")]/following-sibling::td/text()')

    #     excess_milage_charge = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Excess Mileage Charge")]/following-sibling::td/text()')

    #     FixedInterestRate_RateofinterestPA = self.getTexts(response, '//div[@class="wrapperInner"]//table//tbody/tr/th[contains(text(), "Interest Rate per annum fixed") or contains(text(), "Interest Rate Per Annum Fixed")]/following-sibling::td/text()')

    #     offer_text = self.getTextAll(response, '//div[@class="wrapperInner"]/p[contains(text(), "ordered between") or contains(text(), "registration and delivery") or contains(text(), "orders from") or contains(text(), "egistered by")]/text()')
    #     if  offer_text:
    #         offerExp = offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
    #         OfferExpiryDate = self.dateMatcher(offerExp)[2]
    #     else:
    #         OfferExpiryDate = 'N/A'


    #     i = 0
    #     for x in monthly_payment:
    #         monthly_payments = x
    #         if "PCP" in carModel[i]:
    #             TypeofFinance = 'Personal Contract Purchase'
    #         elif "HP" in carModel[i]:
    #             TypeofFinance = 'Hire Purchase'
    #         else:
    #             TypeofFinance = 'Personal Contract Purchase'
    #         car_make = 'Honda'
    #         item = CarItem()
    #         item['CarMake'] = car_make
    #         # print("url", item['CarModel'])
    #         if "20YM" in carModel[i]:
    #             item['CarModel'] = self.remove_special_char_on_excel(carModel[i].split("20YM")[1])
    #         else:
    #             item['CarModel'] = self.remove_special_char_on_excel(carModel[i])
    #         # item['TypeofFinance'] = self.get_type_of_finance('PCP')
    #         item['TypeofFinance'] = TypeofFinance
    #         item['MonthlyPayment'] = self.make_two_digit_no(monthly_payments)
    #         item['CustomerDeposit'] = self.remove_gbp(customer_deposit[i])
    #         try:
    #             if retailer_deposit_contribution:
    #                 item['RetailerDepositContribution']  = self.remove_gbp(retailer_deposit_contribution[i]).replace(",", "")
    #             else:
    #                 item['RetailerDepositContribution']  = 'N/A'
    #         except:
    #               pass
    #         if len(on_the_road_price) > 1:
    #             item['OnTheRoadPrice'] = self.remove_gbp(on_the_road_price[i]).replace(",", "")
    #         else:
    #             item['OnTheRoadPrice'] = 'N/A'
    #         item['AmountofCredit'] = self.remove_gbp(amount_of_credit[i]).replace(",", "")
    #         if len(durations) > 1:
    #             item['DurationofAgreement'] = durations[i].split("months")[0]
    #         else:
    #             item['DurationofAgreement'] = 'N/A'

    #         try:
    #             if OptionalPurchase_FinalPayment:
    #                 item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment[i]).replace(",", "")
    #             else:
    #                 item['OptionalPurchase_FinalPayment']  = 'N/A'
    #         except:
    #             pass

    #         item['TotalAmountPayable'] = self.remove_gbp(total_amount_payable[i])
    #         try:
    #             if len(PurchaseActivationFee) > 1:
    #                 item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(PurchaseActivationFee[i])
    #             else:
    #                 item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
    #         except:
    #             pass
    #         if len(representative_apr) > 1:
    #             item['RepresentativeAPR'] = self.remove_percentage_sign(representative_apr[i])
    #         else:
    #             item['RepresentativeAPR'] = 'N/A'
    #         item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA[i])
    #         try:
    #             if excess_milage_charge:
    #                 item['ExcessMilageCharge'] = self.remove_gbp(excess_milage_charge[i])
    #             else:
    #                 item['ExcessMilageCharge'] = 'N/A'
    #         except:
    #             pass

    #         try:
    #             if average_miles_per_year:
    #                 item['AverageMilesPerYear'] = self.remove_percentage_sign(average_miles_per_year[i])
    #             else:
    #                 item['AverageMilesPerYear'] = 'N/A'
    #         except:
    #             pass
    #         if len(on_the_road_price) > 1:
    #             item['RetailCashPrice'] = self.remove_gbp(on_the_road_price[i]).replace(",", "")
    #         else:
    #             item['RetailCashPrice'] = 'N/A'
    #         item['OfferExpiryDate'] = OfferExpiryDate
    #         item['WebpageURL'] = response.url
    #         item['CarimageURL'] = car_image
    #         item['DebugMode'] = self.Debug_Mode
    #         try:
    #             item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         except:
    #             item['FinalPaymentPercent'] = float()
    #         try:
    #             item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
    #         except:
    #             item['DepositPercent'] = float()
    #         i += 1
    #         if item['MonthlyPayment'] != '' and item['CarModel'] != '':
    #             yield item
