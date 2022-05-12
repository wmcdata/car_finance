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


class MaseratiSpider(BaseSpider):
    name = "maserati.com"
    allowed_domains = []
    holder = list()
    start_url = 'https://www.maserati.com/gb/en/shopping-tools/current-offers'
    base_url = 'https://www.maserati.com'

    def __init__(self):
        super(MaseratiSpider, self).__init__()
        self.i = 0

    def start_requests(self):
        """ Start request
        """
        yield Request(self.start_url, callback=self.parse_category, headers=self.headers)

    def parse_category(self,response):
        """ Start Category
        """
        href = self.getTexts(response, '//div[contains(@class, "grid-item")]//a[contains(text(), "MORE DETAILS")]/@href')
        for a in href:
            url = urljoin(response.url, a)
            # print("final_url: ", url)
            # input("wait here:")
            yield Request(url, callback=self.parse_item, headers=self.headers)
            # yield Request("https://www.maserati.com/gb/en/shopping-tools/quattroporte-finance-app-offers", callback=self.parse_item, headers=self.headers)

    def parse_item(self, response):
        """ Function for parse category
        """
        car_model1 = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr[1]/td/b/br/following-sibling::text()') #### Before Br

        car_model1 = self.getTexts(response, '//div[@class="inner-table-container"]/table/thead/tr/th[contains(text(), "Model")]/following-sibling::th/text()') #### Before Br
        if not car_model1:
            car_model1 = self.getTexts(response, '//div[@class="inner-table-container"]/table/thead/tr/th[b[contains(text(), "Model")]]/following-sibling::th/text()') ####
        if not car_model1:
            car_model1 = self.getTexts(response, '//div[@class="inner-table-container"]/table/thead/tr/th[b[contains(text(), "Model")]]/following-sibling::th/b/text()') ####

        if not car_model1:
            car_model1 = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[contains(text(), "Model")]/following-sibling::td/text()') #### FPR PCH

        # print("car_model1: ", car_model1)
        # print("response: ", response.url)
        # input("wait here:")

        # if not car_model1:
        #     car_model1 = self.getTexts(response, '//div[@class="inner-table-container"]/table/thead/tr/th[b[contains(text(), "Model")]]/following-sibling::th/b/text()')
        # car_model2 = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr[1]/td/b/br/preceding-sibling::text()') #### After Br

        # concat_func = lambda x,y: x + " " + str(y)

        # finalModel = list(map(concat_func,car_model2,car_model1)) # list the map function


        car_images = self.getText(response, '//div[@class="image-container"]/div/img/@src')

        OnTheRoadPrice = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "On the Road Price")]]/following-sibling::td//text()')

        CustomerDeposit = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Customer Deposit") or contains(text(), "Initial Payment")]]/following-sibling::td//text()')
        if not CustomerDeposit:
            CustomerDeposit = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[contains(text(), "Initial Rental")]/following-sibling::td//text()')

        AmountofCredit = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Amount of Credit")]]/following-sibling::td//text()')
        
        MonthlyPayment = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Monthly Payment")]]/following-sibling::td//text()')
        if not MonthlyPayment:
            MonthlyPayment = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[contains(text(), "Monthly Rentals")]/following-sibling::td//text()')

        # if MonthlyPayment == []:
        #     MonthlyPayment = []
            # for i in range(len(OnTheRoadPrice)):
            #     # Append each number at the end of list
            #     MonthlyPayment.append(i)

        OptionalPurchase_FinalPayment = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Optional Final Payment")]]/following-sibling::td//text()')

        TotalAmountPayable = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Total Amount Payable")]]/following-sibling::td//text()')

        DurationofAgreement = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Duration of Contract") or contains(text(), "Term")]]/following-sibling::td//text()')
        if not DurationofAgreement:
            DurationofAgreement = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[contains(text(), "Duration of Contract")]/following-sibling::td//text()')

        AverageMilesPerYear = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Annual Mileage")]]/following-sibling::td//text()')
        if not AverageMilesPerYear:
            AverageMilesPerYear = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[contains(text(), "Annual Mileage")]/following-sibling::td//text()')

        FixedInterestRate_RateofinterestPA = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Rate of Interest")]]/following-sibling::td//text()')

        RepresentativeAPR = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "APR")]]/following-sibling::td//text()')

        RetailerDepositContribution = self.getTexts(response, '//div[@class="inner-table-container"]/table/tbody/tr/td[b[contains(text(), "Maserati Deposit Contribution")]]/following-sibling::td//text()')

        text_path = self.getTextAll(response, '//div[@class="description"]//p[contains(text(), "Offer available") or contains(text(), "registered between")]/text()')
        if text_path:    
            regex = r'(31st|30th|29th|28th) ([Jj]an(uary)?|[Ff]eb(ruary)?|[Mm]ar(ch)?|[Aa]pr(il)?|[Mm]ay|[Jj]une?|[Jj]uly?|[Aa]ug(ust)?|[Ss]ept?(ember)?|[Oo]ct(ober)?|[Nn]ov(ember)?|[Dd]ec(ember)?) (\d{4})?|(\d{1,2}[- ]+[A-Za-z]{3,}[- ]+\d{2,4})|(\b\d{1,2}\/[\d]{1,2}\/\d{2,4})|(\d{2}-[\d]+-\d{2,4})'
            resultSearch = re.findall(regex, text_path)[1]
            offerExp = [x.strip() for x in resultSearch if x.strip()][0]
            OfferExpiryDate = datetime.strptime(offerExp, "%d/%m/%y").strftime('%d/%m/%Y')
        else:
            OfferExpiryDate = '30/06/2022'    



        # print("MonthlyPayment: ", MonthlyPayment)
        # print("OnTheRoadPrice: ", OnTheRoadPrice)
        # print("resp: ", response.url)
        # input("wait here:")

        # expirydate = text_path.split("registered between")[1].split(".")[0]
        # offerExp = expirydate.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        # OfferExpiryDate = self.dateMatcher(offerExp)

        # if "and" in expirydate:
        #     OfferExpiryDate = expirydate.split("and")[1]
        # elif "until" in expirydate:
        #     OfferExpiryDate = expirydate.split("until")[1]
        # AverageMilesPerYear_text = text_path.split("exceeding ")[1].split("miles ")[0]
        if "be charged " in text_path:
            ExcessMilageCharge = text_path.split("be charged ")[1].split("p")[0]
        else:
            ExcessMilageCharge = '12'


        finance_type = self.getTextAll(response, '//div[@class="text"]/h2[@class="title"]/text()')
        if "Personal Contact Purchase" in finance_type:
            TypeofFinance = 'PCP'
        elif "Hire Purchase" in finance_type:
            TypeofFinance = 'Hire Purchase'
        else:
            TypeofFinance = 'PCP'


        if "-app-offers" in response.url:
            AverageMilesPerYears = '15000'
        else:
            AverageMilesPerYears = '8000'        
        # print("car_model2: ", car_model2)
        # print("text_path: ", resultSearch)
        # print("resp: ", response.url)
        # input("wait here:")

        i = 0
        if len(MonthlyPayment) == 0:
            for x in OnTheRoadPrice:
                monthlyPayment = 0
                car_make = "Maserati"
                item = CarItem()
                item['CarMake'] = car_make
                item['CarModel'] = self.remove_special_char_on_excel(car_model1[i])
                item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
                item['MonthlyPayment'] = 0
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit[i])
                if RetailerDepositContribution:
                    item['RetailerDepositContribution'] = self.make_two_digit_no(RetailerDepositContribution[i])
                else:
                    item['RetailerDepositContribution'] = 'N/A'
                if OnTheRoadPrice:
                    item['OnTheRoadPrice'] = self.remove_gbp(x)
                else:
                    item['OnTheRoadPrice'] = 'N/A'
                if OptionalPurchase_FinalPayment:
                    item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment[i])
                else:
                    item['OptionalPurchase_FinalPayment'] = 'N/A'
                if AmountofCredit:
                    item['AmountofCredit'] = self.remove_gbp(AmountofCredit[i])
                else:
                    item['AmountofCredit'] = 'N/A'
                item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement[i])
                if TotalAmountPayable:
                    item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable[i])
                else:
                    item['TotalAmountPayable'] = 'N/A'
                item['OptionToPurchase_PurchaseActivationFee'] =  ''

                if RepresentativeAPR:
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR[i])
                else:
                    item['RepresentativeAPR'] = 'N/A'
                if FixedInterestRate_RateofinterestPA:
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA[i])
                else:
                    item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                if AverageMilesPerYears:
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYears)
                else:
                    item['AverageMilesPerYear'] = 'N/A'
                if OnTheRoadPrice:
                    item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice[i])
                else:
                    item['RetailCashPrice'] = 'N/A'
                item['CarimageURL'] = car_images
                item['OfferExpiryDate'] = OfferExpiryDate
                item['DebugMode'] = self.Debug_Mode
                item['WebpageURL'] = response.url
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                i += 1
                yield item
        else:
            for x in MonthlyPayment:
                monthlyPayment = x
                car_make = "Maserati"
                item = CarItem()
                item['CarMake'] = car_make
                item['CarModel'] = self.remove_special_char_on_excel(car_model1[i])
                item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
                item['MonthlyPayment'] =self.make_two_digit_no(monthlyPayment)
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit[i])
                if RetailerDepositContribution:
                    item['RetailerDepositContribution'] = self.make_two_digit_no(RetailerDepositContribution[i])
                else:
                    item['RetailerDepositContribution'] = 'N/A'
                if OnTheRoadPrice:
                    item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice[i])
                else:
                    item['OnTheRoadPrice'] = 'N/A'
                if OptionalPurchase_FinalPayment:
                    item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment[i])
                else:
                    item['OptionalPurchase_FinalPayment'] = 'N/A'
                if AmountofCredit:
                    item['AmountofCredit'] = self.remove_gbp(AmountofCredit[i])
                else:
                    item['AmountofCredit'] = 'N/A'
                item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement[i])
                if TotalAmountPayable:
                    item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable[i])
                else:
                    item['TotalAmountPayable'] = 'N/A'
                item['OptionToPurchase_PurchaseActivationFee'] =  ''

                if RepresentativeAPR:
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR[i])
                else:
                    item['RepresentativeAPR'] = 'N/A'
                if FixedInterestRate_RateofinterestPA:
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA[i])
                else:
                    item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                if AverageMilesPerYears:
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYears)
                else:
                    item['AverageMilesPerYear'] = 'N/A'
                if OnTheRoadPrice:
                    item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice[i])
                else:
                    item['RetailCashPrice'] = 'N/A'
                item['CarimageURL'] = car_images
                item['OfferExpiryDate'] = OfferExpiryDate
                item['DebugMode'] = self.Debug_Mode
                item['WebpageURL'] = response.url
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                i += 1
                yield item
