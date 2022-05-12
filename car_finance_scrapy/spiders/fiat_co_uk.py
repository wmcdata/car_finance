# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
# from scrapy import log
import urllib
import json
from datetime import datetime, timedelta
from time import gmtime, strftime
from dateutil.relativedelta import relativedelta
import re
import locale
from urllib.parse import urljoin
from html.parser import HTMLParser
from requests import Session

class FiatCars(BaseSpider):
    name = "fiat.co.uk"

    allowed_domains = []
    holder = list()
    base_url  = 'http://www.fiat.co.uk'
    start_url = ['https://www.fiat.co.uk/new-car-deals', 'https://www.fiat.co.uk/business-car-contract-hire-offers', 'https://www.fiatprofessional.com/uk/promotions']

    def __init__(self):
        super(FiatCars, self).__init__()

    def start_requests(self):
        """ Start request
        """
        for url in self.start_url:
            if "new-car-deals" in url:
                yield Request(url, callback=self.parse_links, headers=self.headers)
            if "business-car-contract-hire-offers" in url:
                yield Request(url, callback=self.parse_business_ch, headers=self.headers, dont_filter=True)
            if "fiatprofessional" in url:
                # print("url", response.url)
                # input()
                yield Request(url, callback=self.parse_vans, headers=self.headers, dont_filter=True)

    # def start_requests(self):
    #     """ Start request
    #     """
    #     yield Request(self.start_url, callback=self.parse_links, headers=self.headers)

    def parse_links(self, response):
        """ PCP AND PCH
        """
        for a in response.xpath('//div[@class="promo-panel-results row padding-bottom-65"]//div[@class="col-xs-12 col-sm-6 col-md-4 result-container padding-check"]//div[@class="editorial-box" or @class="editorial-box-content"]'):
            half_link =  self.getText(a, './a/@href')
            href = "https://www.fiat.co.uk" + half_link
            # print("date_text", len(href))
            # print("href", href)
            # input("stop")
            yield Request(href, callback=self.parse_more_link, headers=self.headers)


    def parse_business_ch(self, response):
        """ BUSINESS CONTRACT HIRE
        """
        # print("href", response.url)
        # input("stop")
        for a in response.xpath('//div[@class="wrap-editorial-box"]//div[contains(@class, "editorial-box")]'):
            half_link =  self.getText(a, './/a/@href')
            href = "https://www.fiat.co.uk" + half_link
            if "business-car-contract-hire" in href:
                yield Request(href, callback=self.parse_bch_offers, headers=self.headers)


    def parse_bch_offers(self, response):
        """
        Function for Scraping BCH OFFERS
        """
        CarimageURL = self.getText(response, '//img/@src')

        monthpriceText = self.getText(response, '//h2[@class="bold"]/text()')
        regex = r"[\$|€|£\20AC\00A3]{1}\d+(?:,\d+){0,2}"
        MonthlyPayment = re.search(regex, monthpriceText).group()

        bchOffersData= self.getText(response, '//div[@data-p2c="description(richtext)"]/p[contains(text(), "Business Contract Hire.")]/text()')
        if not bchOffersData:
            bchOffersData= self.getTextAll(response, '//div[@data-p2c="description(richtext)"]/p/text()')
        # print("bchOffersData", bchOffersData)
        # print("href", response.url)
        # input("stop")

        model = bchOffersData.split("Hire.")[1]
        if ". " in model:
            CarModel = model.split(". ")[0]
        if "from " in model:
            CarModel = model.split("from ")[0]
            ###############################
        
        
        if " initial rental." in bchOffersData:
            CustomerDeposit = bchOffersData.split(" initial rental.")[0].split("plus £")[1]
            DurationofAgreement = '36'
        elif "initial rental," in bchOffersData:
            CustomerDeposit = bchOffersData.split("initial rental,")[0].split("plus £")[1]
            DurationofAgreement = '36'    
        else:
            CustomerDeposit = 'N/A'
            DurationofAgreement = '36'   
        if "nitial rental of " in bchOffersData:
            initial = bchOffersData.split("nitial rental of ")[1]
            if "followed by" in initial:
                CustomerDeposit = initial.split("followed by")[0]
                DurationofAgreement = '35'
            elif "." in initial:
                CustomerDeposit = initial.split(".")[0]
                DurationofAgreement = '36'
 

        # print("CarModel", CarModel)
        # print("bchOffersData", MonthlyPayment)
        # print("CustomerDeposit", CustomerDeposit)
        # print("DurationofAgreement", DurationofAgreement)
        # print("response", response.url)
        # input("stop")

        TypeofFinance = 'BCH'
        carMake = 'Fiat'
        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = self.remove_special_char_on_excel(CarModel)
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        item['MonthlyPayment'] = self.reText(MonthlyPayment, r'([\d\.\,]+)')
        item['CustomerDeposit'] = self.remove_percentage_sign(self.reText(CustomerDeposit, r'([\d\.\,]+)'))
        item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = 'N/A'
        item['AmountofCredit'] = 'N/A'
        item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
        item['OptionalPurchase_FinalPayment'] = 'N/A'
        item['TotalAmountPayable'] = 'N/A'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = 'N/A'
        item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        item['ExcessMilageCharge'] = 'N/A'
        item['AverageMilesPerYear'] = "8000"
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = 'N/A'
        item['WebpageURL'] = response.url
        item['CarimageURL'] = CarimageURL
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        # except:
        #     item['DepositPercent'] = float()
        yield item



    def parse_more_link(self, response):
        """ start_urls
        """
        multipleLinks = response.xpath('//div[@class="promo-panel-results row"]//div[@class="col-xs-12 col-sm-6 col-md-4 result-container vertical-spacing fiat-show"]')
        if multipleLinks:
            for a in multipleLinks:
                half_link =  self.getText(a, './/a/@href')
                href = "https://www.fiat.co.uk" + half_link
                # print("date_text", len(href))
                # print("href", href)
                # input("stop")
                yield Request(href, callback=self.parse_car_item, headers=self.headers, dont_filter=True)
        else:
            # print("href", response.url)
            # input("stop")
            yield Request(response.url, callback=self.parse_car_item, headers=self.headers, dont_filter=True)

    def parse_car_item(self, response):
        """ Function for parse item
        """
        CarimageURL = self.getText(response, '//div[@id="hero-fiat"]//img/@src')
        tablePath = response.xpath('//div[@id="accordionFiat"]//div[@class="card panel"]')
        for table in tablePath:
            CarModel = self.getText(table, './/div[@class="card-header"]/div/text()')
            MonthlyPayment = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "Monthly Payment")]/following-sibling::div/text()')
            CustomerDeposit = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "Customer Deposit") or contains(text(), "Initial Rental")]/following-sibling::div/text()')
            OnTheRoadPrice = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "On the Road Price") or contains(text(), "On The Road Price")]/following-sibling::div/text()')
            DepositContribution = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "Fiat Deposit Contribution") or contains(text(), "Fiat Deposite Contribution")]/following-sibling::div/text()')
            AmountofCredit = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "Amount of Credit")]/following-sibling::div/text()')
            DurationofAgreement = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "Duration of Contract")]/following-sibling::div/text()')
            OptionalPurchase_FinalPayment = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "Optional Final Payment")]/following-sibling::div/text()')
            TotalAmountPayable = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "Total Amount Payable")]/following-sibling::div/text()')
            FixedInterestRate_RateofinterestPA = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "Rate of Interest")]/following-sibling::div/text()')
            RepresentativeAPR = self.getText(table, './/div[@class="table"]/div[@class="table-row"]//div[contains(text(), "APR")]/following-sibling::div/text()')

            finance = self.getText(response, '//div[@class="countdown-title-above"]/text()')
            if "PCP" in finance:
                TypeofFinance = 'Personal Contract Purchase'
            elif "PCH" in finance:
                TypeofFinance = 'Personal Contract Hire'
            else:
                TypeofFinance = 'Personal Contract Hire'
            carMake = 'Fiat'
            item = CarItem()
            item['CarMake'] = carMake
            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = self.reText(MonthlyPayment, r'([\d\.\,]+)')
            item['CustomerDeposit'] = self.remove_percentage_sign(self.reText(CustomerDeposit, r'([\d\.\,]+)'))
            if not item['CustomerDeposit']:
                item['CustomerDeposit'] = 'N/A'
            item['RetailerDepositContribution'] = self.remove_percentage_sign(self.reText(DepositContribution, r'([\d\.\,]+)'))
            if not item['RetailerDepositContribution']:
                item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = self.remove_percentage_sign(self.reText(OnTheRoadPrice, r'([\d\.\,]+)'))
            if not item['OnTheRoadPrice']:
                item['OnTheRoadPrice'] = 'N/A'
            item['AmountofCredit'] = self.remove_percentage_sign(self.reText(AmountofCredit, r'([\d\.\,]+)'))
            item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
            item['OptionalPurchase_FinalPayment'] = self.remove_percentage_sign(self.reText(OptionalPurchase_FinalPayment, r'([\d\.\,]+)'))
            item['TotalAmountPayable'] = self.remove_percentage_sign(self.reText(TotalAmountPayable, r'([\d\.\,]+)'))
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = self.remove_percentage_sign(self.remove_percentage_sign(RepresentativeAPR))
            item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
            item['ExcessMilageCharge'] = '6'
            item['AverageMilesPerYear'] = '6000'
            item['OfferExpiryDate'] = '30/06/2022'
            # item['OfferExpiryDate'] = OfferExpiryDate
            item['RetailCashPrice'] = self.remove_percentage_sign(self.reText(OnTheRoadPrice, r'([\d\.\,]+)'))
            item['WebpageURL'] = response.url
            item['CarimageURL'] = CarimageURL
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            if item['CarModel'] != '' and item['MonthlyPayment'] != '':
                yield item


            ##### FIAT Professional VANS start here#####
            ##### FIAT Professional VANS start here#####
            ##### FIAT Professional VANS start here#####

    def parse_vans(self, response):
        """
        Function for parse Url
        """
        link = response.xpath('//div[@class="slider-container promotions-columns-slider-container"]//div[@class="tile-container"]')
        for a in link:
            href = response.urljoin(self.getText(a, './/a/@href'))
            if "doblo" in href or "talento" in href or "ducato" in href or "fiorino" in href or "e-ducato" in href:
                yield Request(href, callback=self.parse_van_more_link, headers=self.headers)

    def parse_van_more_link(self, response):
        """
        Function for parse Url
        """
        links = ['https://www.fiatprofessional.com/uk/promotions/offer/doblo-bch', 'https://www.fiatprofessional.com/uk/promotions/offer/ducato-bch', 'https://www.fiatprofessional.com/uk/promotions/offer/fiorino-bch', 'https://www.fiatprofessional.com/uk/promotions/offer/e-ducato-bch']
        for href in links:
        # link = response.xpath('//div[@class="container flex-container model-slider-container slider-container "]//div[@class="promo-container"]')
        # for a in link:
        #     href = response.urljoin(self.getText(a, './/a/@href'))
            # promoCategory = self.getText(a, './/div[@class="promo-tag"]/text()')
            # if "555 OFFER" not in promoCategory:
                # print("href: ", href)
                # print("urkl: ", response.url)
                # input("wait3")
            yield Request(href, callback=self.parse_van_items, headers=self.headers)

    def parse_van_items(self, response):
        """
        Function for Scraping Vans data
        """
        CarimageURL = self.getText(response, '//div[@class="promo-container"]//picture//img/@src')
        TypeofFinance = ''

        modelPath = response.xpath('//div[@class="promo-accordion"]//div[@class="accordion-title"]') ###FOR MODEL NAME
        dataPath = response.xpath('//div[@class="promo-accordion"]//div[@class="accordion"]') ### For Prices

        for model in range(len(modelPath)):
            models = self.getTexts(modelPath[model], './/span//text()')
            if len(models) > 1:
                CarModel = models[1]
            else:
                CarModel = 'N/A'
            MonthlyPayment = self.getTexts(dataPath[model], './/div[@class="table"]//div[@class="row row-price"]//div[contains(text(), "monthly rentals of")]/following-sibling::div/text()')[0]
            CustomerDeposit = self.getText(dataPath[model], './/div[@class="table"]//div[@class="row row-price"]//div[contains(text(), "Initial Rental")]/following-sibling::div/text()')
            DurationofAgreement = self.getText(dataPath[model], './/div[@class="table"]//div[@class="row row-price"]//div[contains(text(), "Contract Duration")]/following-sibling::div/text()')
            AverageMilesPerYear = self.getText(dataPath[model], './/div[@class="table"]//div[@class="row row-price"]//div[contains(text(), "Annual Mileage")]/following-sibling::div/text()')


            # if "- " in self.getTexts(modelPath[model], './/span//text()')[0]:
            #     TypeofFinance = self.getTexts(modelPath[model], './/span//text()')[0].split("- ")[1]
            # elif "* " in self.getTexts(modelPath[model], './/span//text()')[0]:
            #     TypeofFinance = self.getTexts(modelPath[model], './/span//text()')[0].split("* ")[1]
            TypeofFinance = 'Commercial Contract Hire'

            # print("MonthlyPayment: ", MonthlyPayment)
            # print("CustomerDeposit: ", CustomerDeposit)
            # print("DurationofAgreement: ", DurationofAgreement)
            # print("AverageMilesPerYear: ", AverageMilesPerYear)
            # print("urkl: ", response.url)
            # input("wait3")


            carMake = 'Fiat Professional'
            item = CarItem()
            item['CarMake'] = carMake
            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = self.reText(MonthlyPayment, r'([\d\.\,]+)')
            item['CustomerDeposit'] = self.remove_percentage_sign(self.reText(CustomerDeposit, r'([\d\.\,]+)'))
            item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = self.remove_percentage_sign(self.remove_percentage_sign(AverageMilesPerYear))
            item['OfferExpiryDate'] = '30/06/2022'
            # item['OfferExpiryDate'] = OfferExpiryDate
            item['RetailCashPrice'] = 'N/A'
            item['WebpageURL'] = response.url
            item['CarimageURL'] = CarimageURL
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            # except:
            #     item['DepositPercent'] = float()
            yield item
