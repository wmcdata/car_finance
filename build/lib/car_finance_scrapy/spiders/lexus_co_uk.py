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

###############PCP AND Contract HIRE BOTH###########################
###############PCP AND Contract HIRE BOTH###########################

class LexusSpider(BaseSpider):
    name = "lexus.co.uk"
    handle_httpstatus_list = [403, 404, 301]
    allowed_domains = []
    holder = list()
    start_url = ['https://www.lexus.co.uk/latest-offers/business', 'https://www.lexus.co.uk/latest-offers/personal']
    base_url = 'https://www.lexus.co.uk'

    def __init__(self):
        super(LexusSpider, self).__init__()
        self.i = 0
        self.XPATH_CATEGORY_LEVEL_1 = '//li[@class="l-component-grid__item  isotope__item js-showMoreItems"]/article/div[@class="c-vehicle-card__content"]'


    #######################################################
    ####################   PCP PCH BCH###################
    ######################################################

    def start_requests(self):
        for url in self.start_url:
            # if "/business/" in url:
            #     # yield Request(url, callback=self.parse_category, headers=self.headersLexus)
            #     yield Request(url, callback=self.parse_category, headers=self.headersLexus, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com"})
            # else:

            # yield Request(url, callback=self.parse_car_link, headers=self.headersLexus)
            yield Request(url, callback=self.parse_car_link, headers=self.headersLexus, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com"})

    def parse_car_link(self, response):
        """ Function for parse Links
        """
     

        linkpath = self.getTexts(response, '//a[contains(@data-gt-label, "View Personal Offers") or contains(@data-gt-label, "View Business Offers")]/@href')
        for a in linkpath:
         
            url = response.urljoin(a)

            # print("url: ", url)
            # # print("url: ", href)
            # # print("car_url: ", response.url)
            # input("wait here:")
            # if "business" in url or "personal" in url:
            yield Request(url, callback=self.parse_car_item, headers=self.headersLexus, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com"})

    def parse_car_item(self, response):
        """ Function for parse item
        """

        # print("car_url: ", response.url)
        # input("wait here:")
        lexusData = response.xpath('//div[@class="cmp-promotion-details"]')
        for ld in lexusData:
            carMake = 'Lexus'
            CarModel = self.getText(ld, './/h3[contains(@class, "title")]/text()')
            CarimageURL = self.getText(ld, './/div/img[@alt="promotion vehicle image"]/@src')
            typeOfFinance = self.getText(ld, './/div[@class="description l-base-text"]/text()')
            MonthlyPayment = self.getText(ld, './/div[contains(text(), "Monthly Payment") or contains(text(), "Monthly Rental") or contains(text(), "Monthly rental")]/following-sibling::div/text()')
            CustomerDeposit = self.getText(ld, './/div[contains(text(), "Customer Deposit") or contains(text(), "Initial Rental")]/following-sibling::div/text()')
            DurationofAgreement = self.getText(ld, './/div[contains(text(), "Term")]/following-sibling::div/text()')
            OnTheRoadPrice = self.getText(ld, './/div[contains(text(), "on the road List Price") or contains(text(), "On the Road Price")]/following-sibling::div/text()')
            RetailerDepositContribution = self.getText(ld, './/div[contains(text(), "Hybrid Deposit Allowance")]/following-sibling::div/text()')
            RepresentativeAPR = self.getText(ld, './/div[contains(text(), "Representative APR")]/following-sibling::div/text()')
            AmountofCredit = self.getText(ld, './/div[contains(text(), "Amount of Credit")]/following-sibling::div/text()')
            OptionalPurchase_FinalPayment = self.getText(ld, './/div[contains(text(), "Optional Final Payment")]/following-sibling::div/text()')
            TotalAmountPayable = self.getText(ld, './/div[contains(text(), "Total Amount Payable")]/following-sibling::div/text()')
            FixedInterestRate_RateofinterestPA = self.getText(ld, './/div[contains(text(), "Fixed Rate of Interest")]/following-sibling::div/text()')
            ExcessMilageCharge = self.getText(ld, './/div[contains(text(), "Excess miles")]/following-sibling::div/text()')
            
            if "Personal Contract Hire" in typeOfFinance:
                DurationofAgreement = '36'
            elif "Business Contract Hire" in  typeOfFinance:
                DurationofAgreement = '48'

            
            AverageMilesPerYear = '8000'

    

            # offer_text = self.getText(response, '//div[@class="c-terms-and-conditions__content"]/p/text()')
            # offerExp = offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
            # OfferExpiryDate = self.dateMatcher(offerExp)[1]
            OfferExpiryDate = '30/06/2022'

            # if "registered and financed by" in offer_text:
            #     OfferExpiryDate = offer_text.split("registered and financed by")[1].split("through Lexus")[0]
            # elif "Financial Services by" in offer_text:
            #     OfferExpiryDate = offer_text.split("Financial Services by")[1].split("on a")[0]


            if "of" in MonthlyPayment or "of" in CustomerDeposit:
                MonthlyPayment = MonthlyPayment.split("of")[0]
                CustomerDeposit = CustomerDeposit.split("of")[0]

            if "Incl" in MonthlyPayment or "Incl" in CustomerDeposit:
                MonthlyPayment = MonthlyPayment.split("Incl")[0]
                CustomerDeposit = CustomerDeposit.split("Incl")[0]
                    

            item = CarItem()
            item['CarMake'] = carMake
            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = self.get_type_of_finance(typeOfFinance)
            item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
            item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
            item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
            item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
            item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
            item['DurationofAgreement'] = DurationofAgreement
            item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
            item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = RepresentativeAPR.replace("%*", "")
            item['FixedInterestRate_RateofinterestPA'] = FixedInterestRate_RateofinterestPA
            item['ExcessMilageCharge'] = ExcessMilageCharge.replace("p","")
            item['AverageMilesPerYear'] = AverageMilesPerYear
            item['OfferExpiryDate'] = OfferExpiryDate
            item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
            item['WebpageURL'] = response.url
            item['CarimageURL'] = CarimageURL
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            if (MonthlyPayment == 0 or MonthlyPayment == "") and (CustomerDeposit == 0 or CustomerDeposit == ""):
                pass
            else:
                yield item
    #######################################################
    ###################### PCP ###########################
    ######################################################

    # def parse_category(self, response):
    #     # body = response.xpath('//li[@class="l-component-grid__item  isotope__item js-showMoreItems"]/article/div[@class="c-vehicle-card__content"]/a[@class="c-vehicle-card__content-link"]/@href').extract()
    #     # print("body: ", body)
    #     # input("wait here:")
    #     for href in response.xpath(self.XPATH_CATEGORY_LEVEL_1):

    #         otr_price = self.getText(href, './/span[@itemprop="price"]/text()')
    #         url = self.getText(href, './a[@class="c-vehicle-card__content-link js-vehicle-grid-item"]/@href')
    #         car_url = self.base_url+url+"/offers/"
    #         # print("car_url: ", car_url)
    #         # input("wait here:")
    #         yield Request(car_url, callback=self.parse_item, headers=self.headersLexus, meta={"otr_price":otr_price, 'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com"})

    # def parse_item(self, response):
    #     On_The_Road_Prices = response.meta['otr_price']
    #     if "from:" in On_The_Road_Prices:
    #         On_The_Road_Prices = On_The_Road_Prices.split("from:")[1]
    #     elif "From:" in On_The_Road_Prices:
    #         On_The_Road_Prices = On_The_Road_Prices.split("From:")[1]
    #     else:
    #         On_The_Road_Prices = On_The_Road_Prices

    #     for li in response.xpath('//ul[@class="l-section__content"]/li[@class="l-section__content-item l-section__content-item--vertical-margin"]'):
    #         car_image_url = li.xpath('.//div[@class="c-finance-details__image"]/picture/img/@src').extract()
    #         car_make = "Lexus"
    #         # OfferExpiryDate = str()
    #         # offer_text = self.getText(response, '//div[@class="c-terms-and-conditions__content"]/p/text()')
    #         # offerExp = offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
    #         # OfferExpiryDate = self.dateMatcher(offerExp)[1]
    #         OfferExpiryDate = '30/06/2022'
    #         # if "registered and financed by" in offer_text:
    #         #     OfferExpiryDate = offer_text.split("registered and financed by")[1].split("through Lexus")[0]
    #         # elif "Financial Services by" in offer_text:
    #         #     OfferExpiryDate = offer_text.split("Financial Services by")[1].split("on a")[0]

    #         # OfferExpiryDate = OfferExpiryDate.split(" 2017 and")[1].split(" and registered")[0]
    #         # print("OfferExpiryDate : ", OfferExpiryDate.split(" 2017 and")[1].split(" and registered")[0])
    #         # input("wait here:")
    #         car_model = self.getText(li, './/h3[@class="c-finance-intro__grade-name"]/text()').strip()
    #         # print("OfferExpiryDate: ", OfferExpiryDate)
    #         # input("wait here:")
    #         type_of_finance = self.getText(li,'.//h4[@class="c-finance-intro__submodel"]/text()').strip()
    #         finance_table_values_personal = li.xpath('.//table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td/text()').extract()
    #         #finance_table_values_buisness = li.xpath('.//table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--equal-spacing ui-table--text-alignment"]/tbody[@class="l-col--medium-6 l-col--xsmall-12"]//td/txt()').extract()
    #         if not finance_table_values_personal:
    #             finance_table_values_personal = li.xpath('.//div[@class="c-finance-business__table"]/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--equal-spacing ui-table--text-alignment"]//td/text()').extract()
    #             keys, values = finance_table_values_personal[::2], finance_table_values_personal[1::2]
    #             dictionary = dict(zip(keys, values))
    #             if "Monthly rental*^:" in dictionary:
    #                 monthly_payment = dictionary['Monthly rental*^:'].split("+")[0].split("£")[1]
    #             elif "Monthly rental††:" in dictionary:
    #                 monthly_payment = dictionary['Monthly rental††:'].split("+")[0].split("£")[1]
    #                 # print("monthly_payment: ", monthly_payment)
    #                 # input("wait here:")
    #             else:
    #                 monthly_payment = str()
    #             # print("here is empty  finance_table_values_personal")
    #             # input("wait here:")
    #         keys, values = finance_table_values_personal[::2], finance_table_values_personal[1::2]
    #         dictionary = dict(zip(keys, values))

    #         if "Monthly payment" in dictionary:
    #             monthly_payment = dictionary['Monthly payment'].split("£")[1]
    #         elif "Monthly rental††:" in dictionary:
    #             monthly_payment = dictionary['Monthly rental††:'].split("+")[0].split("£")[1]
    #         elif "Monthly rental*^:" in dictionary:
    #             monthly_payment = dictionary['Monthly rental*^:'].split("+")[0].split("£")[1]
    #         else:
    #             monthly_payment = str()
    #         try:
    #             if "Customer Deposit" in dictionary:
    #                 customer_deposit = dictionary['Customer Deposit'].split("£")[1].split(",")
    #                 customer_deposit = int(customer_deposit[0]+customer_deposit[1])
    #             else:
    #                 customer_deposit = str()
    #         except:
    #             # print("here is empty", customer_deposit)
    #             # input("wait here:")
    #             if "Customer Deposit" in dictionary:
    #                 customer_deposit = dictionary['Customer Deposit'].split("£")[1].split(",")
    #                 customer_deposit = float(customer_deposit[0]+customer_deposit[1])
    #             else:
    #                 customer_deposit = str()

    #         if "Total Deposit" in dictionary:
    #             Total_Deposit = dictionary['Total Deposit'].split("£")[1].split(",")
    #             Total_Deposit = int(Total_Deposit[0]+Total_Deposit[1])
    #             # print("Total_Deposit: ", type(int(Total_Deposit)))
    #             # print("customer_deposit: ", type(customer_deposit))
    #             # input("wait here:")
    #             retailer_deposit_contribution = Total_Deposit - customer_deposit
    #         else:
    #             retailer_deposit_contribution = str()
    #         if "Cash Price including customer saving" in dictionary:
    #             on_the_road_price = dictionary['Cash Price including customer saving'].split("£")[1]
    #         else:
    #             on_the_road_price = str()
    #         if "Amount of Credit" in dictionary:
    #             amount_of_credit = dictionary['Amount of Credit'].split("£")[1]
    #         else:
    #             amount_of_credit = str()
    #         if "Term" in dictionary:
    #             duration_of_agreement = dictionary['Term'].split(" ")[0]
    #         else:
    #             duration_of_agreement = str()
    #         if "Total Amount Payable" in dictionary:
    #             total_amount_payable = dictionary['Total Amount Payable'].split("£")[1]
    #         else:
    #             total_amount_payable = str()
    #         if "Option to purchase fee**:" in dictionary:
    #             PurchaseActivationFee = dictionary['Option to purchase fee**:'].split("£")[1]
    #         else:
    #             PurchaseActivationFee = str()
    #         if "Representative APR" in dictionary:
    #             representative_apr = dictionary['Representative APR'].split("%")[0]
    #         else:
    #             representative_apr = str()
    #         if "Fixed Rate of Interest (per annum)" in dictionary:
    #             fixed_intrest_rate = dictionary['Fixed Rate of Interest (per annum)'].split("%")[0]
    #         else:
    #             fixed_intrest_rate = str()
    #         if "Excess miles (over 8,000miles pa) inc. VAT" in dictionary:
    #             excess_milage_charge = dictionary['Excess miles (over 8,000miles pa) inc. VAT']
    #         else:
    #             excess_milage_charge = str()
    #         if "Average miles per year:" in dictionary:
    #             average_miles_per_year = dictionary['Average miles per year:']
    #         else:
    #             average_miles_per_year = str()
    #         if "Cash Price including customer saving" in dictionary:
    #             retail_cash_price = dictionary['Cash Price including customer saving'].split("£")[1]
    #         else:
    #             retail_cash_price = str()
    #         if "Manufacturer List Price" in dictionary:
    #             on_the_road_price = dictionary['Manufacturer List Price'].split("£")[1]
    #         else:
    #             on_the_road_price = str()


    #         if "Guaranteed Future Value / Optional Final Payment " in dictionary:
    #             OptionalPurchase_FinalPayment = dictionary['Guaranteed Future Value / Optional Final Payment '].split("£")[1]
    #         else:
    #             OptionalPurchase_FinalPayment =  str()

    #         # monthly_payment = self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Monthly payment")]/following-sibling::td[1]/text()')
    #         # print("car_model: ", car_model)
    #         # print("monthly_payment: ", monthly_payment)
    #         # input("wait here:")

    #         RepresentativeAPR = self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Representative APR")]/following-sibling::td[1]/text()')
    #         if "*" in RepresentativeAPR:
    #             RepresentativeAPR = RepresentativeAPR.split('*')[0]
    #         elif "^" in RepresentativeAPR:
    #             RepresentativeAPR = RepresentativeAPR.split("^")[0]



    #         item = CarItem()
    #         item['CarMake'] = car_make
    #         item['CarModel'] = self.remove_special_char_on_excel(car_model)
    #         item['TypeofFinance'] = self.get_type_of_finance(type_of_finance)
    #         item['MonthlyPayment'] = self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Monthly payment")]/following-sibling::td[1]/text()'))
    #         if item['MonthlyPayment']:
    #             item['MonthlyPayment'] = float(item['MonthlyPayment'])
    #         item['CustomerDeposit'] = self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Customer Deposit")]/following-sibling::td[1]/text()'))
    #         if item['CustomerDeposit']:
    #             item['CustomerDeposit'] = float(item['CustomerDeposit'])

    #         # item['RetailerDepositContribution'] = self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Contribution")]/following-sibling::td[1]/text()'))
    #         # if item['RetailerDepositContribution']:
    #         item['RetailerDepositContribution'] = float()
    #         # item['OnTheRoadPrice'] = self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "List Price")]/following-sibling::td[1]/text()'))
    #         item['OnTheRoadPrice'] = self.remove_gbp(On_The_Road_Prices)
    #         if item['OnTheRoadPrice']:
    #             item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
    #         if not item['OnTheRoadPrice']:
    #             item['OnTheRoadPrice'] = 'N/A'
    #         item['AmountofCredit'] = self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Amount of Credit")]/following-sibling::td[1]/text()'))
    #         item['DurationofAgreement']   = self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Term")]/following-sibling::td[1]/text()')
    #         item['OptionalPurchase_FinalPayment']   = self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Optional Final Payment")]/following-sibling::td[1]/text()'))
    #         item['TotalAmountPayable'] = self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Amount Payable")]/following-sibling::td[1]/text()'))
    #         item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Option to purchase fee")]/following-sibling::td[1]/text()'))
    #         item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
    #         item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Fixed Rate of Interest")]/following-sibling::td[1]/text()'))
    #         ExcessMilageCharge = self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Excess miles")]/following-sibling::td[1]/text()')
    #         item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
    #         item['AverageMilesPerYear'] = '8000'
    #         item['RetailCashPrice'] =self.remove_gbp(self.getText(li, './/table[@class="ui-table ui-table--bold ui-table--no-margin ui-table--no-bottom-border ui-table--text-alignment ui-table--multi-body"]/tbody[@class="l-col--large-4 l-col--xsmall-12"]//td[contains(text(), "Cash Price")]/following-sibling::td[1]/text()'))
    #         # item['OfferExpiryDate'] = OfferExpiryDate.split("and")[1]
    #         item['OfferExpiryDate'] = OfferExpiryDate
    #         item['WebpageURL'] = response.url
    #         item['CarimageURL'] = car_image_url
    #         item['DebugMode'] = self.Debug_Mode
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         try:
    #             item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
    #         except:
    #             item['DepositPercent'] = float()
    #         if item['CarModel'] != '' and  item['MonthlyPayment'] != '':
    #             yield item
