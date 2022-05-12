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


class VolksVansSpider(BaseSpider):
    name = "volkswagen-vans.co.uk"
    allowed_domains = []
    holder = list()
    # https://www.volkswagen-vans.co.uk/en/buy-a-van/offers/caddy-panel-van-offers.html' start url
    start_url = ['https://www.volkswagen-vans.co.uk/en/buy-a-van/offers.html', 'https://www.volkswagen-vans.co.uk/app/local/finance-calculator']
    base_url = 'https://www.volkswagen-vans.co.uk'

    def __init__(self):
        super(VolksVansSpider, self).__init__()
        self.i = 0
        self.XPATH_CATEGORY_LEVEL_1 = '//div[@class="col col-xs-12 col-sm-4"]/div[@class="vw_js_slider_item"]//a/@href'


    def start_requests(self):
        """ Start request
        """
        for url in self.start_url:
            if "offers.html" in url:
                yield Request(url, callback=self.parse_van_url,  headers=self.headers)
            else:
                yield Request(url, callback=self.parse_category, headers=self.headers)
        # yield Request(self.start_url, callback=self.parse_category, headers=self.headers)

    def parse_category(self, response):

        # urls = response.xpath('//ul[@class="vw_m510_nav_list"]/li[@class="vw_m510_nav_item"]/a/@href').extract()
        loop = response.xpath('//div[@class="vw_m200_teaser_content col-xs-12 col-sm-12"]')
        for a in loop:
            url = self.getText(a, './/a[@class="vw_m032_btn_primary btn "]/@href')
            # yield Request(url, callback=self.parse_car_url, headers=self.headers, dont_filter=True)

    def parse_van_url(self, response):

        url_loop = self.getTexts(response, '//a[contains(@class, "StyledLink-sc-afbv6g")]/@href')
        for url in url_loop:
            if "-offers" in url and "aftersales-offers" not in url and "offers/stock-vehicle-offers.html" not in url:
                href = urljoin(response.url, url)
                # print("url", response.url)
                # print("href", href)
                # input("stop")
                yield Request(href, callback=self.get_vans_data, headers=self.headers, dont_filter=True)

    def get_vans_data(self, response):
        """VANS DATA
        """
        # print("url", response.url)
        # # print("conditionCheck: ", conditionCheck)
        # input("stop")
        carmodel = str()
        try:
            carmodel1 = self.getTexts(response, '//span[contains(@class, "StyledTextComponent-sc-hqqa9q")]/span[@class="StyledRichtextComponent-bjeRmS iQWxmb"]/h3//text()')[0]
            # if len(carmodel1) > 0:
                # carmodel1 = carmodel1[0]
            carmodel2 = self.getTexts(response, '//span[contains(@class, "StyledTextComponent-sc-hqqa9q")]/span[@class="StyledRichtextComponent-bjeRmS iQWxmb"]//h3//text()')[1]
        # if len(carmodel2) > 0:
        #     carmodel2 = carmodel2[1]

            carmodel = carmodel1 +' '+ carmodel2
            # print("url", response.url)
            # print("conditionCheck: ", carmodel)
            # print("carmodel1: ", carmodel1)
            # print("carmodel2: ", carmodel2)
            # input("stop")
        except:
            print("in case of if any model has not data")

        # print("conditionCheck: ", carmodel)
        # print("carmodel1: ", carmodel1)
        # print("carmodel2: ", carmodel2)
        # print("carmodel2: ", carmodel2)
        # input("stop")

        if "Transporter 6.1 T32" in carmodel:
            carmodel = 'Transporter 6.1 T32 kombi Highline SWB 2.0TDI 150PS 6-speed manual'
        elif "Grand" in carmodel:
            carmodel = 'Grand California 600 2.0TDI 177PS 8-speed automatic'
        elif "ABT e -" in carmodel:
            carmodel = 'ABT e-Transporter 6.1 Panel van'
        elif "offers/transporter-sportline" in response.url:
            carmodel = 'Transporter 6.1 T32 panel van Sportline SWB 2.0 TDI 204PS DSG'
        else:
            carmodel = carmodel

        TypeofFinanceCheck  = self.getTexts(response, '//span[contains(@class, "StyledTextComponent-sc-hqqa9q")]/span[@class="StyledRichtextComponent-bjeRmS iQWxmb"]/p/sub/b/text()')
        if not TypeofFinanceCheck:
            TypeofFinanceCheck  = self.getTexts(response, '//span[contains(@class, "StyledTextComponent-sc-hqqa9q")]/span[@class="StyledRichtextComponent-bjeRmS iQWxmb"]/p/b/text()')
        # print("url", response.url)
        # print("carmodel: ", carmodel)
        # input("stop 11")
        for conditionCheck in TypeofFinanceCheck:
            # print("url", response.url)
            # print("conditionCheck: ", TypeofFinanceCheck)
            # input("stop 11")
            # if "36 month" in conditionCheck:
            #     DurationofAgreement = '36'
            # elif "48 month" in conditionCheck:
            #     DurationofAgreement = '48'
            # else:
            #     DurationofAgreement = 'N/A'
            if "Contract Hire" in conditionCheck:
                MonthlyPayment = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Monthly rental") or contains(text(), "monthly rentals")]]]]]]/following-sibling::td//text()')
                if not MonthlyPayment:
                    MonthlyPayment = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[span[contains(text(), "Monthly rental") or contains(text(), "monthly rentals")]]]]]]]/following-sibling::td//p//text()')
                CustomerDeposit = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Customer initial rental")]]]]]]/following-sibling::td//text()')
                if not CustomerDeposit:
                    CustomerDeposit = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Customer initial rental")]]]]]]/following-sibling::td//p/text()')
                RetailerDepositContribution = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Initial rental contribution")]]]]]]/following-sibling::td//text()')
                if not RetailerDepositContribution:
                    RetailerDepositContribution = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Initial rental contribution")]]]]]]/following-sibling::td//p/text()')
                OnTheRoadPrice = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "On the road retail cash price")]]]]]]/following-sibling::td//text()')
                if not OnTheRoadPrice:
                    OnTheRoadPrice = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "On the road retail cash price")]]]]]]/following-sibling::td//p/text()')
                ExcessMilageCharge = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Excess mileage charge")]]]]]]/following-sibling::td//text()')
                if not ExcessMilageCharge:
                    ExcessMilageCharge = self.getText(response, '//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Excess mileage charge")]]]]]]/following-sibling::td//p/text()')

                # if 'ABT e-Transporter 6.1 Panel van' in carmodel:
                #     OfferExpiryDate = '30th June 2021'
                # else:
                OfferExpiryDate = '31/03/2022'


                car_make = "volkswagen"
                item = CarItem()
                item['CarMake'] = car_make
                item['WebpageURL'] = response.url
                item['CarimageURL'] = 'N/A'
                item['CarModel'] = carmodel
                item['TypeofFinance'] =  self.get_type_of_finance('Commercial Contract Hire')
                item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                if CustomerDeposit:
                    item['CustomerDeposit'] = self.make_two_digit_no(str(CustomerDeposit))
                else:
                    item['CustomerDeposit'] = 'N/A'
                item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
                item['OnTheRoadPrice'] = item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
                item['DurationofAgreement'] = '48'
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                item['OptionalPurchase_FinalPayment'] = 'N/A'
                item['AverageMilesPerYear'] = 'N/A'
                item['OfferExpiryDate'] = OfferExpiryDate
                item['TotalAmountPayable'] = 'N/A'
                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                item['RepresentativeAPR'] = 'N/A'
                item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                item['AmountofCredit'] = 'N/A'
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                yield item

            elif "Personal Contract Plan" in conditionCheck or "Hire Purchase" in conditionCheck:

                MonthlyPayment = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "monthly payments of") or contains(text(), "Monthly payments")]]]]]]/following-sibling::td//text()')
                if not MonthlyPayment:
                    MonthlyPayment = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "monthly payments of") or contains(text(), "Monthly payments")]]]]]]/following-sibling::td//p/text()')
                CustomerDeposit = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Customer deposit")]]]]]]/following-sibling::td//text()')
                if not CustomerDeposit:
                    CustomerDeposit = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Customer deposit")]]]]]]/following-sibling::td//p/text()')
                RetailerDepositContribution = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Deposit contribution")]]]]]]/following-sibling::td//text()')
                if not RetailerDepositContribution:
                    RetailerDepositContribution = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Deposit contribution")]]]]]]/following-sibling::td//p/text()')
                OnTheRoadPrice = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "On the road retail cash price")]]]]]]/following-sibling::td//text()')
                if not OnTheRoadPrice:
                    OnTheRoadPrice = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "On the road retail cash price")]]]]]]/following-sibling::td//p/text()')
                ExcessMilageCharge = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Excess mileage charge (incl. VAT)")]]]]]]/following-sibling::td//text()')
                if not ExcessMilageCharge:
                    ExcessMilageCharge = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Excess mileage charge (incl. VAT)")]]]]]]/following-sibling::td//p/text()')

                TotalAmountPayable = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Total amount payable")]]]]]]/following-sibling::td//text()')
                if not TotalAmountPayable:
                    TotalAmountPayable = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Total amount payable")]]]]]]/following-sibling::td//p/text()')
                AmountofCredit = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Total amount of credit ")]]]]]]/following-sibling::td//text()')
                if not AmountofCredit:
                    AmountofCredit = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Total amount of credit")]]]]]]/following-sibling::td/div/div/span/p//text()')
                RepresentativeAPR = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Representative APR")]]]]]]/following-sibling::td//text()')
                if not RepresentativeAPR:
                    RepresentativeAPR = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Representative APR")]]]]]]/following-sibling::td//p/text()')
                FixedInterestRate_RateofinterestPA = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Rate of interest")]]]]]]/following-sibling::td//text()')
                if not FixedInterestRate_RateofinterestPA:
                    FixedInterestRate_RateofinterestPA = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Rate of interest")]]]]]]/following-sibling::td//p/text()')
                OptionToPurchase_PurchaseActivationFee = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Option to purchase fee^")]]]]]]/following-sibling::td//text()')
                if not OptionToPurchase_PurchaseActivationFee:
                    OptionToPurchase_PurchaseActivationFee = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Option to purchase fee^")]]]]]]/following-sibling::td//p/text()')
                OptionalPurchase_FinalPayment = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Optional final payment")]]]]]]/following-sibling::td//text()')
                if not OptionalPurchase_FinalPayment:
                    OptionalPurchase_FinalPayment = self.getText(response,'//table[@class="StyledTable-dfhxxR fnserG"]//tbody/tr/th[div[div[span[span[p[contains(text(), "Optional final payment")]]]]]]/following-sibling::td//p/text()')

                # if 'ABT e-Transporter 6.1 Panel van' in carmodel:
                #     OfferExpiryDate = '30/04/2021'
                # else:
                OfferExpiryDate = '30/06/2022'

                # print("MonthlyPayment: ", MonthlyPayment)
                # # print("CustomerDeposit: ", CustomerDeposit)
                # # print("RetailerDepositContribution: ", RetailerDepositContribution)
                # print("OnTheRoadPrice: ", OnTheRoadPrice)
                # print("url: ", response.url)
                # input("wait hrer")
                if "Personal Contract Plan" in conditionCheck:
                    TypeofFinance = 'Personal Contract Purchase'
                elif  "Hire Purchase" in conditionCheck:
                    TypeofFinance = 'Hire Purchase'
                car_make = "volkswagen"
                item = CarItem()
                item['CarMake'] = car_make
                item['WebpageURL'] = response.url
                item['CarimageURL'] = 'N/A'
                item['CarModel'] = carmodel
                item['TypeofFinance'] =  self.get_type_of_finance(TypeofFinance)
                item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
                item['OnTheRoadPrice'] = item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
                item['DurationofAgreement'] = '36'
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
                item['AverageMilesPerYear'] = '10000'
                item['OfferExpiryDate'] = OfferExpiryDate
                item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
                item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(OptionToPurchase_PurchaseActivationFee)
                item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                yield item




#             def remove_empty_string(self, listitem):
#                 item = list(filter(None, listitem))
#                 return item
#             def list_to_dict(self, key, value):
#                 lenth_of_keys = len(key)
#                 lenth_of_values = len(value)
#                 divident = int(lenth_of_values/lenth_of_keys)
#                 values = list(self.chunks(value, divident))
#                 a=[]
#                 count=0
#                 for _ in range(divident):
#                     count_inner = 0
#                     for val in values:
#                         try:
#                             dic = dict([(key[count_inner],val[count])])
#                         except:
#                             pass
#                         a.append(dic)
#                         count_inner +=1
#                     count +=1
#                 a = list(self.chunks(a, lenth_of_keys))
#                 return a
#
#             def chunks(self, l, n):
#                 for i in range(0, len(l), n):
#                     yield l[i:i+n]
# `
