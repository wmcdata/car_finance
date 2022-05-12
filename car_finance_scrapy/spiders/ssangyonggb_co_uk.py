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

class SSangYong(BaseSpider):
    name = "ssangyong_co_uk"
    allowed_domains = []
    holder = list()
    start_url = 'https://www.ssangyonggb.co.uk/contents/ssangyong-offers'
    base_url = 'https://www.ssangyonggb.co.uk/'

    def __init__(self):
        super(SSangYong, self).__init__()
        self.i = 0

    def start_requests(self):
        """ Start request
        """
        yield Request( self.start_url, callback=self.parse_pcp_links, headers=self.headers)

    def parse_pcp_links(self, response):
        """ PCP OFFERS
        """
        linkdata = response.xpath('//div/a[contains(@class, "new-model-item flex-height")]')
        for a in linkdata:
            href = self.getText(a, './/@href')
            url = urljoin(response.url, href)
            # url = url +"offers"
            # print("ur", url)
            # input("stop")
            yield Request(url, callback=self.parse_next_link, headers=self.headers)

    def parse_next_link(self, response):
        """ PCP OFFERS
        """
        linkdata = self.getTexts(response, '//a[contains(text(), "More Details")]/@href')
        for a in linkdata:
            url = urljoin(response.url, a)
            if "affiliate-programme" not in url:
                # print("resp", response.url)
                # print("myurl", url)
                # input("stop")
                yield Request(url, callback=self.parse_for_data, headers=self.headers)

    def parse_for_data(self, response):
        """ PCP OFFERS here
        """
        # print("url:", response.url)
        # input("wait here:")


        # CarimageURL = self.getText(response, '//div[@class="page__content_wrapper"]/img/@src')
        i = 0

        MonthlyPayment = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Monthly Payments of") or contains(text(), "Monthly payments of") or con]/following-sibling::td/text()')
        if not MonthlyPayment:
            MonthlyPayment = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Monthly Payments of") or contains(text(), "Monthly payments of")]]/following-sibling::td/text()')

        OnTheRoadPrice = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "On-the-road cash Price is now") or contains(text(), "On-the-Road") or contains(text(), "On-the-road")]/following-sibling::td/text()')
        if not OnTheRoadPrice:
            OnTheRoadPrice = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "On-the-road cash Price is now") or contains(text(), "On-the-Road") or contains(text(), "On-the-road")]]/following-sibling::td/text()')
        CustomerDeposit = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Customer Deposit") or contains(text(), "Customer deposit")]/following-sibling::td/text()')
        if not CustomerDeposit:
            CustomerDeposit = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Customer Deposit") or contains(text(), "Customer deposit")]]/following-sibling::td/text()')

        AmountofCredit = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Total Amount of Credit") or contains(text(), "Total amount of credit")]/following-sibling::td/text()')
        if not AmountofCredit:
            AmountofCredit = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Total Amount of Credit") or contains(text(), "Total amount of credit")]]/following-sibling::td/text()')
        TotalAmountPayable = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Total Amount Payable") or contains(text(), "Total amount payable")]/following-sibling::td/text()')
        if not TotalAmountPayable:
            TotalAmountPayable = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Total Amount Payable") or contains(text(), "Total amount payable")]]/following-sibling::td/text()')
        FixedInterestRate_RateofinterestPA = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Fixed Rate of Interest") or contains(text(), "Fixed rate of interest")]/following-sibling::td/text()')
        if not FixedInterestRate_RateofinterestPA:
            FixedInterestRate_RateofinterestPA = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Fixed Rate of Interest") or contains(text(), "Fixed rate of interest")]]/following-sibling::td/text()')
        AnnualMileage = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Mileage Per Annum") or contains(text(), "Mileage per Annum")]/following-sibling::td/text()')
        if not AnnualMileage:
            AnnualMileage = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Mileage Per Annum") or contains(text(), "Mileage per Annum")]]/following-sibling::td/text()')
        ExcessMilageCharge = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Excess Mileage charge")]/following-sibling::td/text()')
        if not ExcessMilageCharge:
            ExcessMilageCharge = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Excess Mileage charge")]]/following-sibling::td/text()')
        DurationofAgreement = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Duration of Agreement") or contains(text(), "Duration of agreement")]/following-sibling::td/text()')
        if not DurationofAgreement:
            DurationofAgreement = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Duration of Agreement") or contains(text(), "Duration of Agreement")]]/following-sibling::td/text()')

        RetailerDepositContribution = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "SsangYong Deposit Contribution") or contains(text(), "Deposit Contribution")]/following-sibling::td/text()')
        if not RetailerDepositContribution:
            RetailerDepositContribution = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "SsangYong Deposit Contribution") or contains(text(), "Deposit Contribution")]]/following-sibling::td/text()')


        RepresentativeAPR = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "APR Representative") or contains(text(), "APR")]/following-sibling::td/text()')
        if not RepresentativeAPR:
            RepresentativeAPR = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "APR Representative")]]/following-sibling::td/text()')
        OptionalPurchase_FinalPayment = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Optional Final Payment") or contains(text(), "Final Payment")]/following-sibling::td/text()')
        if not OptionalPurchase_FinalPayment:
            OptionalPurchase_FinalPayment = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Optional Final Payment") or contains(text(), "Final Payment")]]/following-sibling::td/text()')

        OptionToPurchase_PurchaseActivationFee = self.getTexts(response, '//table/tbody/tr//td[contains(text(), "Option to purchase fee")]/following-sibling::td/text()')
        if not OptionToPurchase_PurchaseActivationFee:
            OptionToPurchase_PurchaseActivationFee = self.getTexts(response, '//table/tbody/tr//td[p[contains(text(), "Option to purchase fee")]]/following-sibling::td/text()')
        modelName = self.getText(response, '//div[@class="banner-text"]//h1/text()')
        if "available on" in modelName:
            modelName = modelName.split("available on ")[1].split(" ")[0]
        # if not model:
        #     model = self.getText(response, '//div[@class="page__content_banner"]//h1/text()')
        # if not model:
        #     model = self.getText(response, '//div[@id="tech"]//h1/text()')



        TermsandConditions = self.getText(response, '//p[contains(text(), "Hire Purchase") or contains(text(), "Personal Contract Purchase")]')

        # print("model", model)
        # print("modelName", modelName)
        # print("item", response.url)
        # input("stop")

        if "Personal Contract Purchase" in TermsandConditions or "PERSONAL CONTRACT PURCHASE" in TermsandConditions:
            TypeofFinance = 'PCP'
        elif "Hire Purchase" in TermsandConditions or "HIRE PURCHASE" in TermsandConditions:
            TypeofFinance = 'HP'
        else:
            TypeofFinance = 'N/A'


        # offerExpText = response.xpath('//p[span[contains(text(), "Terms and Conditions")]]/following-sibling::p/text()').extract()[0]
        # if offerExpText != []:
        #     offerExp = offerExpText.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        #     OfferExpiryDate = self.dateMatcher(offerExp)[0]
        # else:
        #     offerExpText = response.xpath('//p[contains(text(), "Terms and Conditions")]/following-sibling::p//text()').extract()[0]
        #     offerExp = offerExpText.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        #     OfferExpiryDate = self.dateMatcher(offerExp)[0]

        # if "angyong/musso/business-contract-hire" in response.url:
        # #     # print("item", modelName)
        #     print("MonthlyPayment", MonthlyPayment)
        #     print("OnTheRoadPrice", OnTheRoadPrice)
        # #     # print("CustomerDeposit", CustomerDeposit)
        # #     # print("AmountofCredit", AmountofCredit)
        # #     # print("TotalAmountPayable", TotalAmountPayable)
        # #     # print("FixedInterestRate_RateofinterestPA", FixedInterestRate_RateofinterestPA)
        # #     # print("OptionToPurchase_PurchaseActivationFee", OptionToPurchase_PurchaseActivationFee)
        # #     # # print("RetailerDepositContribution", RetailerDepositContribution)
        # print("offerExpText", offerExpText)
        # print("item", response.url)
        # input("stop")

        # updated_response = response.replace(body=response.body.replace(b'<br>', b''))
        for a,x in enumerate(MonthlyPayment):
            if a == 0:
                j = 2
            # carmodel_var = ' '.join(self.getTexts(response, '//table/tbody/tr/th['+str(j)+']//text()'))
            j += 1
            MonthlyPayments = x
            item = CarItem()
            item['CarMake'] = 'SSangYong'
            # if "0%" in modelName:
            #     item['CarModel'] = self.remove_special_char_on_excel(modelName.split("0%")[0])
            # else:
            item['CarModel'] = self.remove_special_char_on_excel(modelName)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = self.make_two_digit_no(self.reText(MonthlyPayments, r'([\d\.\,]+)'))
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit[i])
            if RetailerDepositContribution != []:
                item['RetailerDepositContribution'] = self.make_two_digit_no(RetailerDepositContribution[i])
            else:
                item['RetailerDepositContribution'] = 'N/A'    
            item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice[i])
            if OptionalPurchase_FinalPayment != []:
                item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment[i])
            else:
                item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['AmountofCredit'] = self.remove_gbp(AmountofCredit[i])
            item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement[i])
            item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable[i])
            if OptionToPurchase_PurchaseActivationFee != []:
                item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(OptionToPurchase_PurchaseActivationFee[i])
            else:
                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'    
            if RepresentativeAPR[i]:
                item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR[i])
            else:
                item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA[i])
            if ExcessMilageCharge != []:
                item['ExcessMilageCharge'] = self.remove_gbp(ExcessMilageCharge[i])
            else:
                item['ExcessMilageCharge'] = 'N/A'
            if AnnualMileage != []:
                item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage[i])
            else:
                item['AverageMilesPerYear'] = 'N/A'
            item['OfferExpiryDate'] = "30/06/2022"
            item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice[i])
            item['CarimageURL'] = ''
            item['WebpageURL'] = response.url
            item['DebugMode'] = self.Debug_Mode
            try:
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            except:
                item['FinalPaymentPercent'] = float()
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            i += 1
            yield item
