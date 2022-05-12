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

 # response.xpath('//table/tbody/tr[contains(@style, "height:")]/td[span[contains(text(), "Cash Price")]]/following-sibling::td').extract()

# response.xpath('//button[contains(text(), "PCP Finance With Deposit")]/following-sibling::div//table/tbody/tr[contains(@style, "height:")]/td[contains(text(), "Model")]/fo
    # ...: llowing-sibling::td').extract()
### PCP Cars
### HIRE Purchase
# response.xpath('//button[contains(text(), "PCP Finance With Deposit")]/following-sibling::div[@class="accordion__panel"][2]//table/tbody/tr/td[contains(text(), "Deposit")]
    # ...: /following-sibling::td//text()').extract()

 # https://cars.suzuki.co.uk/umbraco/Surface/FinanceCalculator/GradeFinanceOptions?financeType=PCP&allowSwap=False&gradeId=fa4082cc-2c4f-46d7-8d1f-d3d4c0db772c
# https://cars.suzuki.co.uk/umbraco/Surface/FinanceCalculator/FinanceQuote
class SuzukiCars(BaseSpider):
    name = "suzuki.co.uk"

    base_url  = 'https://www.suzuki.co.uk/'
    # start_url = 'https://cars.suzuki.co.uk/offers-finance/'
    start_url = ['https://cars.suzuki.co.uk/offers-finance/', 'https://cars.suzuki.co.uk/']

    ### Car both PCP and BCH

    def __init__(self):
        super(SuzukiCars, self).__init__()

    # def start_requests(self):
    #     yield Request(self.start_url, callback=self.parse_car, headers=self.headers)

    def start_requests(self):
        for url in self.start_url:
            if "/offers-finance/" in url:
                yield Request(url, callback=self.parse_hp_pcp_cars, headers=self.headers) ### HIRE PURCHASE
            else:
                yield Request(url, callback=self.parse_pcp_strong_tag_url, headers=self.headers) ### HIRE PURCHASE

    def parse_hp_pcp_cars(self, response):
        """HIRE PURCHASE / PCP Without Strong offer url
        """
        link = self.getTexts(response, '//a[contains(@class, "{ button button--primary }") or contains(@alt, "Explore ")]/@href')
        for a in link:
            # href = self.getText(a, './/a[contains(@class, "cta-button "]/@href')
            url = response.urljoin(a)
            if "offers-finance/" in url and "/suzuki-finance/" not in url:
                # print("url", response.url)
                # print("jO", url)
                # input("stop")
                yield Request(url, callback=self.parse__hp_pcp_model, headers=self.headers)
####################################3
####################################
    def parse_pcp_strong_tag_url(self, response):
        """PCP STRONG
        """
        href = 'https://cars.suzuki.co.uk/offers-finance/'
        yield Request(href, callback=self.parse_pcp_strong_model, headers=self.headers, dont_filter = True)

    def parse_pcp_strong_model(self, response):
        """PCP CARS URLS STRONG
        """
        link = self.getTexts(response, '//a[contains(@class, "{ button button--primary }") or contains(@alt, "Explore ")]/@href')
        for a in link:
            url = response.urljoin(a)
            if "offers-finance/" in url and "/suzuki-finance/" not in url:
                # print("url", response.url)
                # print("jO", url)
                # input("stop")
                # urls ='https://cars.suzuki.co.uk/offers-finance/vitara-offers-and-finance/'
                yield Request(url, callback=self.parse_pcp_strong_car_data, headers=self.headers, dont_filter = True)

####################################3
####################################
    def parse__hp_pcp_model(self, response):
        """HIRE PURCHASE offer data
        """
        financeType = ["PCP", "HP"]
        for type in financeType:
            if "HP" in type:
                yield Request(response.url, callback=self.HP_parse_strong_car_data, headers=self.headers, dont_filter = True)
            if "HP" in type:
                CarimageURL = self.getText(response, '//div[@class="content-module-full-width--image"]/@data-images')

                MonthlyPayments = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Monthly Payments of") or contains(text(), "monthly payments") or contains(text(), "monthly payment")]/following-sibling::td/text()')
                # MonthlyPayments2 = MonthlyPayments2.replace("£","")

                carModel = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[2]/td/text()')
                if "swift-sport-offers-and-finance" in response.url or "/across-offers-and-finance" in response.url:
                    carModel = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[1]/td/text()')
                
                carModels = [x.strip() for x in carModel if x.strip()]
                

                customer_deposit = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[not(contains(text(), "Finance Deposit Allowance")) and contains(text(), "Deposit")]/following-sibling::td/text()')
                on_the_road_price = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Cash price") or contains(text(), "Customer Saving Cash Price") or contains(text(), "Cash Price")]/following-sibling::td/text()')
                amount_of_credit = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/text()')
                total_amount_payable = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/text()')
                Duration = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Duration of agreement")]/following-sibling::td/text()')
                APR = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "APR")]/following-sibling::td/text()')

                

                
                OptionToPurchase_PurchaseActivationFee = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Purchase Fee")]]/following-sibling::td/text()')
                if not OptionToPurchase_PurchaseActivationFee:
                    OptionToPurchase_PurchaseActivationFee = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Purchase Fee")]/following-sibling::td//text()')

                FixedInterestRate_RateofinterestPA = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Interest Rate")]]/following-sibling::td/span/text()')
                if not FixedInterestRate_RateofinterestPA:
                    FixedInterestRate_RateofinterestPA = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Interest Rate") or contains(text(), "Interest rate")]/following-sibling::td//text()')

                # print("URL",response.url)
                # print("CarimageURL",CarimageURL)
                # print("MonthlyPayments2",MonthlyPayments)
                # print("carModels",carModels)
                # print("customer_deposit",customer_deposit)
                # print("on_the_road_price",on_the_road_price)
                # print("amount_of_credit",amount_of_credit)
                # print("total_amount_payable",total_amount_payable)
                # print("Duration",Duration)
                # print("APR",APR)
                # print("FixedInterestRate_RateofinterestPA",FixedInterestRate_RateofinterestPA)
                # input("wait befor")

                i = 0
                for x in MonthlyPayments:
                    MonthlyPayment = x
                    try:
                        CarModelAll = carModels[i]
                    except Exception as e:
                        print("this is a exception in HP CarModelAll",e)
                    try:
                        CustomerDeposit = customer_deposit[i]
                    except Exception as e:
                        print("this is a exception in HP CustomerDeposit",e)
                    try:
                        OnTheRoadPrice = on_the_road_price[i]
                    except Exception as e:
                        print("this is a exception in HP OnTheRoadPrice",e)
                    # try:
                    #     OptionalPurchase_FinalPayment = finalpayment[i]
                    # except Exception as e:
                    #     print("this is a exception in OptionalPurchase_FinalPayment",e)
                    try:
                        OptionToPurchase_PurchaseActivationFees = OptionToPurchase_PurchaseActivationFee[i]
                    except Exception as e:
                        print("this is a exception in HP OptionToPurchase_PurchaseActivationFee",e)
                    try:
                        AmountofCredit = amount_of_credit[i]
                    except Exception as e:
                        print("this is a exception in HP AmountofCredit",e)
                    try:
                        TotalAmountPayable = total_amount_payable[i]
                    except Exception as e:
                        print("this is a exception in HP TotalAmountPayable",e)
                    try:
                        DurationofAgreement = Duration[i]
                    except Exception as e:
                        print("this is a exception in HP DurationofAgreement",e)
                    try:
                        RepresentativeAPR = APR[i]
                    except Exception as e:
                        print("this is a exception in HP RepresentativeAPR",e)
                    try:
                        FixedInterestRate_Rateofinteresthp = FixedInterestRate_RateofinterestPA[i]
                    except Exception as e:
                        print("this is a exception in HP RepresentativeAPR",e)

                        
                    i += 1

                    # print("URL",response.url)
                    # print("CarimageURL",CarimageURL)
                    # print("MonthlyPayment",MonthlyPayment)
                    # print("CarModelAll",CarModelAll)
                    # print("CustomerDeposit",CustomerDeposit)
                    # print("OptionToPurchase_PurchaseActivationFees",OptionToPurchase_PurchaseActivationFees)
                    # print("OnTheRoadPrice",OnTheRoadPrice)
                    # print("AmountofCredit",AmountofCredit)
                    # print("TotalAmountPayable",TotalAmountPayable)
                    # print("DurationofAgreement",DurationofAgreement)
                    # print("RepresentativeAPR",RepresentativeAPR)
                    # print("FixedInterestRate_Rateofinteresthp",FixedInterestRate_Rateofinteresthp)
                    # # input("wait after")
                    

                    item = CarItem()
                    item['CarMake'] = 'Suzuki'
                    item['CarModel'] = self.remove_special_char_on_excel(CarModelAll)
                    item['TypeofFinance'] = self.get_type_of_finance('Hire Purchase')
                    item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
                    item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
                    item['RetailerDepositContribution'] =  'N/A'
                    item['OnTheRoadPrice'] =  self.remove_gbp(OnTheRoadPrice)
                    item['OptionalPurchase_FinalPayment'] =  'N/A'
                    item['AmountofCredit'] =   self.remove_gbp(AmountofCredit)
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                    item['TotalAmountPayable'] =  self.remove_gbp(TotalAmountPayable)
                    if OptionToPurchase_PurchaseActivationFees:
                        item['OptionToPurchase_PurchaseActivationFee'] =  self.remove_gbp(OptionToPurchase_PurchaseActivationFees)
                    else:
                        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                    # item['FixedInterestRate_Rateofinteresthp'] = self.remove_percentage_sign(FixedInterestRate_Rateofinteresthp)
                    item['ExcessMilageCharge'] = 'N/A'
                    item['AverageMilesPerYear'] = 'N/A'
                    item['OfferExpiryDate'] = '31/03/2022'
                    item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice)
                    item['CarimageURL'] = CarimageURL
                    item['WebpageURL'] = response.url
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    if item['MonthlyPayment'] != '':
                        yield item

            elif "PCP" in type:
                
                """PCP
                """
                carImage = self.getText(response, '//div[@class="content-module-full-width--image"]/@data-images')
                CarimageURL = carImage.split('["')[1].split(",")[0]
                MonthlyPayments = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Monthly Payments of") or contains(text(), "monthly payments")]/following-sibling::td/text()')
                MonthlyPayments = [x.strip("£") for x in MonthlyPayments if x.strip("£")]
                carModel = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[2]/td/text()')
                if "swift-sport-offers-and-finance" in response.url or "/across-offers-and-finance" in response.url:
                    carModel = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[1]/td/text()')

                carModels = [x.strip() for x in carModel if x.strip()]

                # print("url", response.url)
                # print("carModels: ", carModels)
                # input("stop")
                customer_deposit = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[not(contains(text(), "Finance Deposit Allowance")) and contains(text(), "Deposit")]/following-sibling::td/text()')
                on_the_road_price = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Cash price") or contains(text(), "Customer Saving Cash Price") or contains(text(), "Cash Price")]/following-sibling::td/text()')
                finalpayment = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Optional Final payment") or contains(text(), "Final payment") or contains(text(), "Optional Final Payment")]/following-sibling::td/text()')
                amount_of_credit = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/text()')
                total_amount_payable = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/text()')
                Duration = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Duration of agreement")]/following-sibling::td/text()')
                APR = self.getTexts(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "APR")]/following-sibling::td/text()')

                

                AverageMilesPerYear = self.getText(response, '//div[@class="rich-text-editor"]/p[contains(text(), "miles per annum")]/text()')
                if not AverageMilesPerYear:
                    AverageMilesPerYear = self.getText(response, '//div[@class="rich-text-editor"]/p/span[contains(text(), "miles per annum")]/text()')
                # optionPurcahseFee = self.getTexts(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Purchase Fee") or contains(text(), "Option To Purchase Fee")]/following-sibling::td/text()')
                # if optionPurcahseFee:
                #     OptionToPurchase_PurchaseActivationFees = optionPurcahseFee
                if "across-offers-and-finance/" in response.url or "/s-cross-offers-and-finance/":
                    OptionToPurchase_PurchaseActivationFees = '10'
                else:
                    OptionToPurchase_PurchaseActivationFees = '0'


                i = 0
                for x in MonthlyPayments:
                    MonthlyPayment = x
                    # print("url", response.url)
                    # print("OnTheRoadPrice:", on_the_road_price)
                    # print("OnTheRoadPrice:", on_the_road_price[i])
                    # input("stop")
                    try:
                        CustomerDeposit = customer_deposit[i]
                    except Exception as e:
                        print("this is a exception in CustomerDeposit",e)
                    try:
                        OnTheRoadPrice = on_the_road_price[i]
                    except Exception as e:
                        print("this is a exception in OnTheRoadPrice",e)
                    try:
                        OptionalPurchase_FinalPayment = finalpayment[i]
                    except Exception as e:
                        print("this is a exception in OptionalPurchase_FinalPayment",e)
                    try:
                        AmountofCredit = amount_of_credit[i]
                    except Exception as e:
                        print("this is a exception in AmountofCredit",e)
                    try:
                        TotalAmountPayable = total_amount_payable[i]
                    except Exception as e:
                        print("this is a exception in TotalAmountPayable",e)
                    try:
                        DurationofAgreement = Duration[i]
                    except Exception as e:
                        print("this is a exception in DurationofAgreement",e)
                    try:
                        RepresentativeAPR = APR[i]
                    except Exception as e:
                        print("this is a exception in RepresentativeAPR",e)
                    try:
                        CarModelAll = carModels[i]
                    except Exception as e:
                        print("this is a exception in CarModelAll",e)
                    # OptionToPurchase_PurchaseActivationFee = OptionToPurchase_PurchaseActivationFees[i]
                    # print("url", response.url)
                    # # print("MonthlyPayment:", MonthlyPayment)
                    # # # print("CarModelAll:", CarModelAll)
                    # # print("CustomerDeposit:", CustomerDeposit)
                    # print("OnTheRoadPrice:", OnTheRoadPrice)
                    # # print("OptionalPurchase_FinalPayment:", OptionalPurchase_FinalPayment)
                    # # print("AmountofCredit:", AmountofCredit)
                    # # print("TotalAmountPayable:", TotalAmountPayable)
                    # # print("DurationofAgreement:", DurationofAgreement)
                    # # print("RepresentativeAPR:", RepresentativeAPR)
                    # # # print("OptionToPurchase_PurchaseActivationFee:", OptionToPurchase_PurchaseActivationFee)
                    # input("stop")

                    item = CarItem()
                    item['CarMake'] = 'Suzuki'
                    item['CarModel'] = self.remove_special_char_on_excel(CarModelAll)
                    item['TypeofFinance'] = self.get_type_of_finance('PCP')
                    item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
                    item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
                    item['RetailerDepositContribution'] =  'N/A'
                    item['OnTheRoadPrice'] =  self.remove_gbp(OnTheRoadPrice)
                    item['OptionalPurchase_FinalPayment'] =  self.remove_gbp(OptionalPurchase_FinalPayment)
                    item['AmountofCredit'] =   self.remove_gbp(AmountofCredit)
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                    item['TotalAmountPayable'] =  self.remove_gbp(TotalAmountPayable)
                    item['OptionToPurchase_PurchaseActivationFee'] =  self.remove_percentage_sign(OptionToPurchase_PurchaseActivationFees)
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                    item['FixedInterestRate_RateofinterestPA'] = ""
                    item['ExcessMilageCharge'] = '4.8'
                    if AverageMilesPerYear:
                        item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
                    else:
                        item['AverageMilesPerYear'] = 'N/A'
                    item['OfferExpiryDate'] = '31/03/2022'
                    item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice)
                    item['CarimageURL'] = CarimageURL
                    item['WebpageURL'] = response.url
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    i += 1
                    if item['MonthlyPayment'] != '':
                        yield item

    def HP_parse_strong_car_data(self, response):
        print("URL",response.url)
        # input("wait")

        carImage = self.getText(response, '//div[@class="content-module-full-width--image"]/@data-images')
        CarimageURL = carImage.split('["')[1].split(",")[0]

        # carmodel = self.getText(response, '//h1[@class="heading-set"]/span/text()')
        try:
            carmodel = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr[2]/td[2]//text()[not(contains(text(),"Representative Example"))]')
        except:
            carmodel = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr[1]/td[2]//text()[not(contains(text(),"Representative Example"))]')

        if "Finance Example" in carmodel:
            try:
                carmodel = self.getText(response, '//div[@class="rich-text-editor"]/p[contains(text(), "Model shown: ")]/text()').split("Model shown: ")[1].split("£")[0]
            except:
                # carmodel = self.getText(response, '//div[@class="t-and-c-footer"]/p[@class="text--smallscript"]/text()').split("Model Shown: ")[1].replace("£","").replace("†","")
                try:
                    carmodel = self.getText(response, '//div[@class="table-container"]//tr[2]/td[2]/text()').split("Model Shown: ")[1].replace("£","").replace("†","")
                except:
                    carmodel = self.getText(response, '//div[@class="table-container"]//tr[2]/td[2]/text()')

        if "swift-sport-offers-and-finance" in response.url:
            carmodel = 'SWIFT 1.4 BOOSTJET HYBRID SPORT'
        
        if "vitara-offers-and-finance/" in response.url and carmodel =='Representative Example':
            carmodel = 'VITARA 1.4 BOOSTERJET MILD HYBRID SZT'

        # if "ignis-offers-and-finance/" in response.url and carmodel =='Representative Example':
        #     carmodel = 'Ignis 1.2 Dualjet Mild Hybrid SZ3'

        # MonthlyPayment = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[span[contains(text(), "Monthly Repayments") or contains(text(), "monthly payments")]]/following-sibling::td/span/text()')
        # if not MonthlyPayment:
        #     MonthlyPayment = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[contains(text(), "Monthly payments") or contains(text(), "Monthly Repayments") or contains(text(), "Monthly Payments") or contains(text(), "monthly payments")]/following-sibling::td//text()')


        MonthlyPayment = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Monthly Repayments") or contains(text(), "monthly payments")]]/following-sibling::td/span/text()')
        if not MonthlyPayment:
            MonthlyPayment = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Monthly payments") or contains(text(), "Monthly Repayments") or contains(text(), "Monthly Payments") or contains(text(), "monthly payments")]/following-sibling::td/strong/text()')


        CustomerDeposit = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Deposit")]]/following-sibling::td/span/strong/text()')
        if not CustomerDeposit:
            CustomerDeposit = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[not(contains(text(), "Finance Deposit Allowance")) and contains(text(), "Deposit")]/following-sibling::td/strong/text()')
        # print("url", response.url)
        # print("CustomerDeposit", CustomerDeposit)
        # input("stop")
        OnTheRoadPrice = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Cash price")]]/following-sibling::td/span/strong/text()')
        if not OnTheRoadPrice:
            OnTheRoadPrice = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Cash price") or contains(text(), "Cash Price")]/following-sibling::td/strong/text()')

        TotalAmountPayable = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Total Amount of Credit")]]/following-sibling::td/span/strong/text()')
        if not TotalAmountPayable:
            TotalAmountPayable = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Total Amount of Credit") or contains(text(), "Total amount of credit")]/following-sibling::td/strong/text()')

        DurationofAgreement = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Duration of agreement")]]/following-sibling::td/span/strong/text()')
        if not DurationofAgreement:
            DurationofAgreement = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Duration of agreement") or contains(text(), "Duration of Agreement")]/following-sibling::td/strong/text()')

        AmountofCredit = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Total Amount of Credit")]]/following-sibling::td/span/strong/text()')
        if not AmountofCredit:
            AmountofCredit = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Total Amount of Credit") or contains(text(), "Total amount of credit")]/following-sibling::td/strong/text()')

        RepresentativeAPR = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "APR")]]/following-sibling::td/span/strong/text()')
        if not RepresentativeAPR:
            RepresentativeAPR = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "APR") or contains(text(), "Representative APR")]/following-sibling::td/strong/text()')

        FixedInterestRate_RateofinterestPA = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Interest Rate")]]/following-sibling::td/span/strong/text()')
        if not FixedInterestRate_RateofinterestPA:
            FixedInterestRate_RateofinterestPA = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Interest Rate") or contains(text(), "Interest rate")]/following-sibling::td/strong/text()')


        OptionToPurchase_PurchaseActivationFee = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[span[contains(text(), "Purchase Fee")]]/following-sibling::td/strong/text()')
        if not OptionToPurchase_PurchaseActivationFee:
            OptionToPurchase_PurchaseActivationFee = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"]//table//tbody/tr/td[contains(text(), "Purchase Fee")]/following-sibling::td/strong/text()')

        
        if "£" in carmodel:
                carmodel = self.getTexts(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire") or contains(text(), "hire")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[1]/td/text()')[1]
        # print("url", response.url)
        # print("carmodel:", carmodel)
        # input("stop")

        item = CarItem()
        item['CarMake'] = 'Suzuki'
        item['CarModel'] = self.remove_special_char_on_excel(carmodel)
        item['TypeofFinance'] = self.get_type_of_finance('Hire Purchase')
        item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
        item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
        item['RetailerDepositContribution'] =  'N/A'
        item['OnTheRoadPrice'] =  self.remove_gbp(OnTheRoadPrice)
        item['OptionalPurchase_FinalPayment'] =  'N/A'
        item['AmountofCredit'] =   self.remove_gbp(AmountofCredit)
        item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
        item['TotalAmountPayable'] =  self.remove_gbp(TotalAmountPayable)
        if OptionToPurchase_PurchaseActivationFee:
            item['OptionToPurchase_PurchaseActivationFee'] =  self.remove_gbp(OptionToPurchase_PurchaseActivationFee)
        else:
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
        item['ExcessMilageCharge'] = 'N/A'
        item['AverageMilesPerYear'] = 'N/A'
        item['OfferExpiryDate'] = '31/03/2022'
        item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice)
        item['CarimageURL'] = CarimageURL
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        if item['MonthlyPayment'] != '':
            yield item
            # input("wait")
        '''
    def HP_parse_strong_car_data(self, response):


        print("URL",response.url)
        input("wait for hp")
        

        """Stronge Tag HP DATA
        """
        carImage = self.getText(response, '//div[@class="content-module-full-width--image"]/@data-images')
        # CarimageURL = carImage.split('["')[1].split(",")[0]
        
        
        MonthlyPayments2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[contains(text(), "Monthly Payments of") or contains(text(), "monthly payments") or contains(text(), "monthly payment")]/following-sibling::td/strong/text()')
        MonthlyPayments2 = MonthlyPayments2.replace("£","")
        
        carModel2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr[2]/td/strong/text()')
        if "swift-sport-offers-and-finance" in response.url or "/across-offers-and-finance" in response.url:
            carModel2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr[1]/td/strong/text()')

        if "vitara-offers-and-finance"in response.url:
            carModel2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr[2]/td/p/strong[not(contains(text(),"Representative Example"))]/text()')
            if not carModel2:
            # if "vitara-offers-and-finance"in response.url or carModel2=="":
                carModel2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr[2]/td/strong[not(contains(text(),"Representative Example"))]/text()')

        # print("carModel2",carModel2)
        # print("URL",response.url)
        # input("wait with bold")
        CustomerDeposit2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[not(contains(text(), "Finance Deposit Allowance")) and contains(text(), "Deposit")]/following-sibling::td/strong/text()')
        OnTheRoadPrice2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[contains(text(), "Cash price") or contains(text(), "Customer Saving Cash Price") or contains(text(), "Cash Price")]/following-sibling::td/strong/text()')
        OptionalPurchase_FinalPayment2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[contains(text(), "Optional Final payment") or contains(text(), "Final payment") or contains(text(), "Optional Final Payment")]/following-sibling::td/strong/text()')
        AmountofCredit2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/strong/text()')
        TotalAmountPayable2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/strong/text()')
        Duration2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[contains(text(), "Duration of agreement")]/following-sibling::td/strong/text()')
        RepresentativeAPR2 = self.getText(response, '//button[span[contains(text(), "Hire Purchase") or contains(text(), "Hire")]]/following-sibling::div[@class="accordion__panel"]/following-sibling::div[@class="accordion__panel"][2]//table//tbody/tr/td[contains(text(), "APR")]/following-sibling::td/strong/text()')
        AverageMilesPerYear2 = self.getText(response, '//div[@class="rich-text-editor"]/p[contains(text(), "miles per annum")]/text()')
        if not AverageMilesPerYear2:
            AverageMilesPerYear2 = self.getText(response, '//div[@class="rich-text-editor"]/p/span[contains(text(), "miles per annum")]/text()')
        # optionPurcahseFee = self.getTexts(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Purchase Fee") or contains(text(), "Option To Purchase Fee")]/following-sibling::td/text()')
        # if optionPurcahseFee:
        #     OptionToPurchase_PurchaseActivationFees = optionPurcahseFee
        if "across-offers-and-finance/" in response.url or "/s-cross-offers-and-finance/":
            OptionToPurchase_PurchaseActivationFees2 = '10'
        else:
            OptionToPurchase_PurchaseActivationFees2 = '0'

        


        item = CarItem()
        item['CarMake'] = 'Suzuki'
        item['CarModel'] = self.remove_special_char_on_excel(carModel2)
        item['TypeofFinance'] = self.get_type_of_finance('Hire Purchase')
        item['MonthlyPayment'] = self.remove_gbp(MonthlyPayments2)
        item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit2)
        item['RetailerDepositContribution'] =  'N/A'
        item['OnTheRoadPrice'] =  self.remove_gbp(OnTheRoadPrice2)
        item['OptionalPurchase_FinalPayment'] =  'N/A'
        item['AmountofCredit'] =   self.remove_gbp(AmountofCredit2)
        item['DurationofAgreement'] = self.remove_percentage_sign(Duration2)
        item['TotalAmountPayable'] =  self.remove_gbp(TotalAmountPayable2)
        if OptionToPurchase_PurchaseActivationFees2:
            item['OptionToPurchase_PurchaseActivationFee'] =  self.remove_gbp(OptionToPurchase_PurchaseActivationFees2)
        else:
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR2)
        item['FixedInterestRate_RateofinterestPA'] = ""
        item['ExcessMilageCharge'] = 'N/A'
        item['AverageMilesPerYear'] = 'N/A'
        item['OfferExpiryDate'] = '31/03/2022'
        item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice2)
        item['CarimageURL'] = carImage
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])

        if item['MonthlyPayment'] != '':
            yield item
        '''

    def parse_pcp_strong_car_data(self, response):
    
        """Stronge Tag PCP DATA
        """
        carImage = self.getText(response, '//div[@class="content-module-full-width--image"]/@data-images')
        # CarimageURL = carImage.split('["')[1].split(",")[0]
        
        
        MonthlyPayments2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Monthly Payments of") or contains(text(), "monthly payments") or contains(text(), "monthly payment")]/following-sibling::td/strong/text()')
        MonthlyPayments2 = MonthlyPayments2.replace("£","")
        
        carModel2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[2]/td/strong/text()')
        if "swift-sport-offers-and-finance" in response.url or "/across-offers-and-finance" in response.url:
            carModel2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[1]/td/strong/text()')

        if "vitara-offers-and-finance"in response.url:
            carModel2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[2]/td/p/strong[not(contains(text(),"Representative Example"))]/text()')
            if not carModel2:
            # if "vitara-offers-and-finance"in response.url or carModel2=="":
                carModel2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[2]/td/strong[not(contains(text(),"Representative Example"))]/text()')

        # print("carModel2",carModel2)
        # print("URL",response.url)
        # input("wait with bold")
        CustomerDeposit2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[not(contains(text(), "Finance Deposit Allowance")) and contains(text(), "Deposit")]/following-sibling::td/strong/text()')
        OnTheRoadPrice2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Cash price") or contains(text(), "Customer Saving Cash Price") or contains(text(), "Cash Price")]/following-sibling::td/strong/text()')
        OptionalPurchase_FinalPayment2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Optional Final payment") or contains(text(), "Final payment") or contains(text(), "Optional Final Payment")]/following-sibling::td/strong/text()')
        AmountofCredit2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/strong/text()')
        TotalAmountPayable2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/strong/text()')
        Duration2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Duration of agreement")]/following-sibling::td/strong/text()')
        RepresentativeAPR2 = self.getText(response, '//button[span[contains(text(), "PCP Finance Without Deposit") or contains(text(), "PCP With Finance Deposit") or contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP Finance With No Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "APR")]/following-sibling::td/strong/text()')
        AverageMilesPerYear2 = self.getText(response, '//div[@class="rich-text-editor"]/p[contains(text(), "miles per annum")]/text()')
        if not AverageMilesPerYear2:
            AverageMilesPerYear2 = self.getText(response, '//div[@class="rich-text-editor"]/p/span[contains(text(), "miles per annum")]/text()')
        # optionPurcahseFee = self.getTexts(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Purchase Fee") or contains(text(), "Option To Purchase Fee")]/following-sibling::td/text()')
        # if optionPurcahseFee:
        #     OptionToPurchase_PurchaseActivationFees = optionPurcahseFee
        if "across-offers-and-finance/" in response.url or "/s-cross-offers-and-finance/":
            OptionToPurchase_PurchaseActivationFees2 = '10'
        else:
            OptionToPurchase_PurchaseActivationFees2 = '0'


        item = CarItem()
        item['CarMake'] = 'Suzuki'
        item['CarModel'] = self.remove_special_char_on_excel(carModel2)
        item['TypeofFinance'] = self.get_type_of_finance('PCP')
        item['MonthlyPayment'] = self.remove_gbp(MonthlyPayments2)
        item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit2)
        item['RetailerDepositContribution'] =  'N/A'
        item['OnTheRoadPrice'] =  self.remove_gbp(OnTheRoadPrice2)
        item['OptionalPurchase_FinalPayment'] =  self.remove_gbp(OptionalPurchase_FinalPayment2)
        item['AmountofCredit'] =   self.remove_gbp(AmountofCredit2)
        item['DurationofAgreement'] = self.remove_percentage_sign(Duration2)
        item['TotalAmountPayable'] =  self.remove_gbp(TotalAmountPayable2)
        item['OptionToPurchase_PurchaseActivationFee'] =  self.remove_percentage_sign(OptionToPurchase_PurchaseActivationFees2)
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR2)
        item['FixedInterestRate_RateofinterestPA'] = ""
        item['ExcessMilageCharge'] = '4.8'
        if AverageMilesPerYear2:
            item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear2)
        else:
            item['AverageMilesPerYear'] = 'N/A'
        item['OfferExpiryDate'] = '31/03/2022'
        item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice2)
        item['CarimageURL'] = carImage
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        if item['MonthlyPayment'] != '':
            yield item


# def parse_pcp_strong_car_data(self, response):            >>>>> NOT WORKING  <<<<<
    
#         """Stronge Tag PCP DATA
#         """
#         # print("stpo", response.url)
#         # input("stop")
#         carImage = self.getText(response, '//div[@class="picture__inner"]/picture//img/@src')
#         MonthlyPayments2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Monthly Payments of") or contains(text(), "monthly payments")]/following-sibling::td/strong/text()')
#         carModel2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[2]/td/strong/text()')
#         if "swift-sport-offers-and-finance" in response.url or "/vitara-offers-and-finance" in response.url:
#             carModel2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[1]/td/strong/text()')
#         # if "/swift-offers-and-finance/" in response.url:
#         #     carModel2 = response.xpath('//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr[2]/td/strong/text()').extract()[1]
#         CustomerDeposit2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[not(contains(text(), "Finance Deposit Allowance")) and contains(text(), "Deposit")]/following-sibling::td/strong/text()')
#         OnTheRoadPrice2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Cash price") or contains(text(), "Customer Saving Cash Price")]/following-sibling::td/strong/text()')
#         OptionalPurchase_FinalPayment2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Optional Final payment") or contains(text(), "Final payment")]/following-sibling::td/strong/text()')
#         AmountofCredit2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/strong/text()')
#         TotalAmountPayable2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/strong/text()')
#         Duration2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Duration of agreement")]/following-sibling::td/strong/text()')
#         RepresentativeAPR2 = self.getText(response, '//button[span[contains(text(), "PCP Finance With Deposit") or contains(text(), "PCP With Finance Deposit")]]/following-sibling::div[@class="accordion__panel"][1]//table//tbody/tr/td[contains(text(), "Representative APR")]/following-sibling::td/strong/text()')
#         AverageMilesPerYear2 = self.getText(response, '//div[@class="rich-text-editor"]/p[contains(text(), "miles per annum")]/text()')
#         if not AverageMilesPerYear2:
#             AverageMilesPerYear2 = self.getText(response, '//div[@class="rich-text-editor"]/p/span[contains(text(), "miles per annum")]/text()')
    
#         # if "vitara-offers-and-finance/" in response.url:
#         #      OptionToPurchase_PurchaseActivationFees2 = '0'
#         if "across-offers-and-finance/" in response.url or "/s-cross-offers-and-finance/":
#             OptionToPurchase_PurchaseActivationFees2 = '10'
#         else:
#             OptionToPurchase_PurchaseActivationFees2 = '0'
    
#         # print("url", response.url)
#         # print("MonthlyPayment:", MonthlyPayments2)
#         # input("sto")
#         item = CarItem()
#         item['CarMake'] = 'Suzuki'
#         item['CarModel'] = self.remove_special_char_on_excel(carModel2)
#         item['TypeofFinance'] = self.get_type_of_finance('PCP')
#         item['MonthlyPayment'] = self.remove_gbp(MonthlyPayments2)
#         item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit2)
#         item['RetailerDepositContribution'] =  'N/A'
#         item['OnTheRoadPrice'] =  self.remove_gbp(OnTheRoadPrice2)
#         item['OptionalPurchase_FinalPayment'] =  self.remove_gbp(OptionalPurchase_FinalPayment2)
#         item['AmountofCredit'] =   self.remove_gbp(AmountofCredit2)
#         item['DurationofAgreement'] = self.remove_percentage_sign(Duration2)
#         item['TotalAmountPayable'] =  self.remove_gbp(TotalAmountPayable2)
#         item['OptionToPurchase_PurchaseActivationFee'] =  self.remove_percentage_sign(OptionToPurchase_PurchaseActivationFees2)
#         item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR2)
#         item['FixedInterestRate_RateofinterestPA'] = ""
#         item['ExcessMilageCharge'] = '4.8'
#         if AverageMilesPerYear2:
#             item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear2)
#         else:
#             item['AverageMilesPerYear'] = 'N/A'
#         item['OfferExpiryDate'] = '30/06/2021'
#         item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice2)
#         item['CarimageURL'] = carImage
#         item['WebpageURL'] = response.url
#         item['DebugMode'] = self.Debug_Mode
#         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
#         item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
#         if item['MonthlyPayment'] != '':
#             yield item
