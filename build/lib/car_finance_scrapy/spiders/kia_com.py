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


class KiaSpider(BaseSpider):
    name = "kia.com"

    allowed_domains = ['kia.com', 'kiafinancecalculator.co.uk']
    base_url = 'https://www.kia.com/'
    start_url = ['https://www.kia.com/uk/new-cars/finance-calculator/', 'https://kia.comcar.co.uk/bch/offers/special']

    # headers
    header_post = {
        'Accept':'application/json, text/plain, */*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.9,vi;q=0.8,und;q=0.7',
        'Connection':'keep-alive',
        'Content-Type':'application/json',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',

    }

    def _getval(self, jO, path, default=''):
        obj = jO
        for p in path.split('>'):
            if '=' in p:
                # filter
                p1,p2 = p.split('=')
                for v in obj:
                    if p1 in v and v[p1] == p2:
                        obj = v
                        break
                if obj != v:
                    return default
            else:
                try:
                    p = int(p)
                except:
                    pass

                try:
                    obj = obj[p]
                except:
                    return default

        return obj

    def __init__(self):
        super(KiaSpider, self).__init__()

    def start_requests(self):
        for url in self.start_url:
            if "/bch/offers/special" in url:
                yield Request(url, callback=self.parse_bch_items_url, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_item, headers=self.headers)

    # def start_requests(self):
    #     for url in self.start_url:
    #         yield Request(url, callback=self.parseLeadOffers,)

    def parse_model_url(self, response):
        car_urls = self.getTexts(response, '//ul[@class="cars new"]/li[starts-with(@class,"car")]/a/@href')
        for href in car_urls:
            href =  response.urljoin(href)
            yield Request(href, callback=self.parse_models, headers=self.headers)


    def parse_models(self, response):
        model_url = self.getTexts(response, '//ul[@class="actions"]/li/a[@class="btn next"]/@href')
        for href in model_url:
            href = response.urljoin(href)
            yield Request(href, callback=self.parse_max_month,  headers=self.headers)

    def parse_bch_items_url(self, response):
        """BCH OFFERS FROM NEW Calculator
        """
        model_url = self.getTexts(response, '//div[contains(@class, "offer-container__links")]/a[contains(text(), "View this offer")]/@href')
        for href in model_url:
            href = response.urljoin(href)
            # print("url", href)
            # input("stop")
            yield Request(href, callback=self.parse_bch_offers_json,  headers=self.headers, dont_filter=True)

    def parse_bch_offers_json(self, response):

        link = response.url
        vehicle_id = response.url.split("vehicle_id=")[1].split("&")[0]
        href = 'https://kia.comcar.co.uk/finance/quote/com/price.cfc?returnFormat=json&method=getSinglePrice&skv_cfg=%7B%22deposit%22%3A%226%22%2C%22months%22%3A%2236%22%2C%22mileage%22%3A%228000%22%2C%22maintenance%22%3A%22No%22%2C%22vehicle_id%22%3A%22'+vehicle_id+'%22%2C%22agreementType%22%3A%22pch%22%2C%22agreement_type_code%22%3A%22bch%22%7D&_=1600087270795'
        yield Request(href, callback=self.parse_bch_get_data, headers=self.headers, dont_filter=True, meta={"link":link})

    def parse_bch_get_data(self, response):
        WebpageURL = response.meta["link"]
        jsondata = json.loads(response.body)
        jsondata = jsondata['data'][0]

        model = jsondata['model']
        derivative = jsondata['derivative']
        CarModel = model +' '+derivative
        MonthlyPayment = jsondata['price']
        CustomerDeposit = round(jsondata['initialpayment'])
        ExcessMilageCharge = jsondata['excess_ppm']
        AverageMilesPerYear = jsondata['mileage']
        DurationofAgreement = jsondata['months']
        TypeofFinance = jsondata['agreementtype']
        # print("data: ", data)
        # print("link: ", link)
        # input("wait here:")

        carMake = 'Kia'
        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = CarModel
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        item['MonthlyPayment'] = MonthlyPayment
        item['CustomerDeposit'] = CustomerDeposit
        item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = 'N/A'
        item['AmountofCredit'] = 'N/A'
        item['DurationofAgreement'] = DurationofAgreement
        item['OptionalPurchase_FinalPayment'] = 'N/A'
        item['TotalAmountPayable'] = 'N/A'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = 'N/A'
        item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        item['ExcessMilageCharge'] = ExcessMilageCharge
        item['AverageMilesPerYear'] = AverageMilesPerYear
        item['OfferExpiryDate'] = '31/03/2022'
        item['RetailCashPrice'] = 'N/A'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = WebpageURL
        item['CarimageURL'] = 'N/A'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


    def parse_max_month(self, response):
        model = response.url.split("model=")[1]
        url = "http://kiafinancecalculator.co.uk/results.aspx?model="+model

        radFinanceOptions = self.getTexts(response, '//ul/li/input[@name="content_0$radFinanceOptions"]/@value')

        radPaymentPeriods = self.getTexts(response, '//ul/li/input[@name="content_0$radPaymentPeriods"]/@value')

        txtDeposit = '1000'
        # txtDeposit = self.getText(response, '//div[@class="cf"]/input[@name="content_0$txtDeposit"]/@value')
        txtEstimatedMileage = '10000'
        # txtEstimatedMileage = self.getText(response, '//ul/li/input[@name="content_0$txtEstimatedMileage"]/@value')
        __LASTFOCUS = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__LASTFOCUS"]/@value')
        __EVENTTARGET = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__EVENTTARGET"]/@value')
        __EVENTARGUMENT = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__EVENTARGUMENT"]/@value')
        __VIEWSTATE = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__VIEWSTATE"]/@value')
        __EVENTVALIDATION = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__EVENTVALIDATION"]/@value')

        on_the_road_price = self.getText(response, '//span[@id="content_0_lblEditionPrice"]/text()')

        for periods in radPaymentPeriods:

            for FinanceOptions in radFinanceOptions:

                formdata = {
                        'content_0$radFinanceOptions':FinanceOptions,
                        'content_0$txtDeposit':txtDeposit,
                        'content_0$radPaymentPeriods':periods,
                        'content_0$txtEstimatedMileage':txtEstimatedMileage,
                        '__ASYNCPOST':'true',
                        'btnCalculate':'Calculate',
                        'btnPaymentsOptionsGo':'Go',
                        '__LASTFOCUS':__LASTFOCUS,
                        '__VIEWSTATE':__VIEWSTATE,
                        '__EVENTARGUMENT':__EVENTARGUMENT,
                        '__EVENTTARGET':__EVENTTARGET,
                        '__EVENTVALIDATION':__EVENTVALIDATION
                        }

                yield FormRequest(response.url, formdata=formdata, callback=self.parse_model, headers=self.headers, dont_filter=True, meta={'on_the_road_price': on_the_road_price, 'txtDeposit': txtDeposit})


    def parse_model(self, response):
        model = response.url.split("model=")[1]
        url = "http://kiafinancecalculator.co.uk/results.aspx?model="+model
        radFinanceOptions = self.getTexts(response, '//ul/li/input[@name="content_0$radFinanceOptions"]/@value')
        radPaymentPeriods = self.getTexts(response, '//ul/li/input[@name="content_0$radPaymentPeriods"]/@value')
        txtDeposit = self.getText(response, '//div[@class="cf"]/input[@name="content_0$txtDeposit"]/@value')
        txtEstimatedMileage = self.getText(response, '//ul/li/input[@name="content_0$txtEstimatedMileage"]/@value')
        __LASTFOCUS = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__LASTFOCUS"]/@value')
        __EVENTTARGET = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__EVENTTARGET"]/@value')
        __EVENTARGUMENT = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__EVENTARGUMENT"]/@value')
        __VIEWSTATE = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__VIEWSTATE"]/@value')
        __EVENTVALIDATION = self.getText(response, '//div[@class="aspNetHidden"]/input[@name="__EVENTVALIDATION"]/@value')
        on_the_road_price = self.getText(response, '//span[@id="content_0_lblEditionPrice"]/text()')
        for periods in radPaymentPeriods:
            for FinanceOptions in radFinanceOptions:

                formdata = {
                        'content_0$radFinanceOptions':FinanceOptions,
                        'content_0$txtDeposit':txtDeposit,
                        'content_0$radPaymentPeriods':radPaymentPeriods,
                        'content_0$txtEstimatedMileage':txtEstimatedMileage,
                        '__ASYNCPOST':'true',
                        'content_0$btnCalculate':'Calculate',
                        '__LASTFOCUS':__LASTFOCUS,
                        '__VIEWSTATE':__VIEWSTATE,
                        '__EVENTARGUMENT':__EVENTARGUMENT,
                        '__EVENTTARGET':__EVENTTARGET,
                        '__EVENTVALIDATION':__EVENTVALIDATION
                        }

                yield FormRequest(url, formdata=formdata, callback=self.parse_item, headers=self.headers, dont_filter=True, meta={'on_the_road_price': on_the_road_price, 'txtDeposit': txtDeposit})

    def parse_item(self, response):
        # print("body: ", response.body)
        # input("wait here:")

        carMake = 'Kia'
        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "The all-new Niro EV '2' 64.8 kWh Long Range EV Automatic"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "408.33"
        item['CustomerDeposit'] = "3499.50"
        item['RetailerDepositContribution'] = '0.00'
        item['OnTheRoadPrice'] = '34995.00'
        item['AmountofCredit'] = '31495.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '20662.50'
        item['TotalAmountPayable'] = '38861.88'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '4.90'
        item['FixedInterestRate_RateofinterestPA'] = '2.52'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '34995.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/newoffers/grid/NiroEV_Nav_240x135.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


        carMake = 'Kia'
        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "The all-new Niro Hybrid '2' 1.6 Petrol Hybrid Automatic DCT"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "341.10"
        item['CustomerDeposit'] = "2774.50"
        item['RetailerDepositContribution'] = '500.00'
        item['OnTheRoadPrice'] = '27745.00'
        item['AmountofCredit'] = '24470.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '15128.75'
        item['TotalAmountPayable'] = '30682.85'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '4.90'
        item['FixedInterestRate_RateofinterestPA'] = '2.52'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '27745.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/newoffers/grid/NiroHEV_Nav_240x135.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item

        carMake = 'Kia'
        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "The all-new Niro Plug-in Hybrid '2' 1.6 Petrol Plug-in Hybrid Automatic DCT"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "426.15"
        item['CustomerDeposit'] = "3277.50"
        item['RetailerDepositContribution'] = '500.00'
        item['OnTheRoadPrice'] = "32775.00"
        item['AmountofCredit'] = '28997.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '17076.25'
        item['TotalAmountPayable'] = '36195.15'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '4.90'
        item['FixedInterestRate_RateofinterestPA'] = '2.52'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = "32775.00"
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/newoffers/grid/NiroPHEV_Nav_240x135.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


        carMake = 'Kia'
        item = CarItem()##  New
        item['CarMake'] = carMake
        item['CarModel'] = "Picanto '1' 1.0 Petrol Manual 4 Seat"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "185.89"
        item['CustomerDeposit'] = "1181.00"
        item['RetailerDepositContribution'] = '750.00'
        item['OnTheRoadPrice'] = "11810.00"
        item['AmountofCredit'] = '9879.00'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '4706.00'
        item['TotalAmountPayable'] = '13329.04'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = "11810.00"
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/ceedsportswagon-2018/kia-ceedsportswagon-2018-2-copper-stone_0000.png.transform/trimimagethumbnail/img.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item

        carMake = 'Kia'
        item = CarItem()##  New
        item['CarMake'] = carMake
        item['CarModel'] = "Rio '1' 1.2 Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "251.23"
        item['CustomerDeposit'] = "1446.00"
        item['RetailerDepositContribution'] = '1250.00'
        item['OnTheRoadPrice'] = "14460.00"
        item['AmountofCredit'] = '11764.00'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '4410.30'
        item['TotalAmountPayable'] = '16150.58'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = "14460.00"
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/ceedsportswagon-2018/kia-ceedsportswagon-2018-2-copper-stone_0000.png.transform/trimimagethumbnail/img.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item

        carMake = 'Kia'
        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "Ceed 'GT-Line' 1.5 Turbocharged Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "345.74"
        item['CustomerDeposit'] = "2498.50"
        item['RetailerDepositContribution'] = '2250.00'
        item['OnTheRoadPrice'] = "24985.00"
        item['AmountofCredit'] = '20236.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '11041.00'
        item['TotalAmountPayable'] = '28236.14'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = "24985.00"
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/ceedsportswagon-2018/kia-ceedsportswagon-2018-2-copper-stone_0000.png.transform/trimimagethumbnail/img.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item

        carMake = 'Kia'
        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "Ceed Sportswagon '2' 1.0 Turbocharged Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "282.52"
        item['CustomerDeposit'] = "2116.50"
        item['RetailerDepositContribution'] = '2250.00'
        item['OnTheRoadPrice'] = '21165.00'
        item['AmountofCredit'] = '16798.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '9344.13'
        item['TotalAmountPayable'] = '23881.35'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '21165.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/ceedsportswagon-2018/kia-ceedsportswagon-2018-2-copper-stone_0000.png.transform/trimimagethumbnail/img.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


        # carMake = 'Kia'
        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "Sportage '2' 1.6 Petrol Manual"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "348.43"
        # item['CustomerDeposit'] = "2478.50"
        # item['RetailerDepositContribution'] = '2500.00'
        # item['OnTheRoadPrice'] = '24785.00'
        # item['AmountofCredit'] = '19806.50'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '9439.20'
        # item['TotalAmountPayable'] = '26961.18'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '4.90'
        # item['FixedInterestRate_RateofinterestPA'] = '2.52'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/03/2022'
        # item['RetailCashPrice'] = '24785.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/sportage_2018/kia-sportage_2018-1-copper-stone_0000.png.transform/trimimagethumbnail/img.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item


        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "The all-new Sorento '2' 1.6 Turbocharged Petrol Self Charging Hybrid Automatic All Wheel Drive 7-seat"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "566.08"
        # item['CustomerDeposit'] = '3936.00'
        # item['RetailerDepositContribution'] = '1000.00'
        # item['OnTheRoadPrice'] = '39360.00'
        # item['AmountofCredit'] = '34424.00'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '17937.60'
        # item['TotalAmountPayable'] = '43252.48'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '4.90'
        # item['FixedInterestRate_RateofinterestPA'] = '2.52'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/12/2021'
        # item['RetailCashPrice'] = '39360.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/sorento-2020/kia-sorento-2020-2-essence-brown_0000.png.transform/trimimagethumbnail/img.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item


        # carMake = 'Kia'
        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "Niro Self-Charging Hybrid 'Connect' 1.6 Petrol Self Charging Hybrid Automatic DCT"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "369.53"
        # item['CustomerDeposit'] = "2629.50"
        # item['RetailerDepositContribution'] = '1750.00'
        # item['OnTheRoadPrice'] = '26295.00'
        # item['AmountofCredit'] = '21915.50'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '11602.50'
        # item['TotalAmountPayable'] = '29285.08'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '5.90'
        # item['FixedInterestRate_RateofinterestPA'] = '3.04'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/03/2022'
        # item['RetailCashPrice'] = '26295.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/niro-hev_2019/kia-niro-hev_2019-2-silky-silver_0000.png.transform/trimimagethumbnail/img.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item


        # carMake = 'Kia'
        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "Niro PHEV 'PHEV 3' 1.6 Plug-in Hybrid Automatic DCT"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "514.84"
        # item['CustomerDeposit'] = "3274.50"
        # item['RetailerDepositContribution'] = '1750.00'
        # item['OnTheRoadPrice'] = '32745.00'
        # item['AmountofCredit'] = '27720.50'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '12808.25'
        # item['TotalAmountPayable'] = '36366.99'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '5.90'
        # item['FixedInterestRate_RateofinterestPA'] = '3.04'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/03/2022'
        # item['RetailCashPrice'] = '32745.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/niro-hev_2019/kia-niro-hev_2019-2-silky-silver_0000.png.transform/trimimagethumbnail/img.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item


        # carMake = 'Kia'
        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "The new Stonic '2' 1.0 Turbocharged Petrol Manual"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "251.76"
        # item['CustomerDeposit'] = "1865.00"
        # item['RetailerDepositContribution'] = '1750.00'
        # item['OnTheRoadPrice'] = '18650.00'
        # item['AmountofCredit'] = '15035.00'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '7659.00'
        # item['TotalAmountPayable'] = '20337.36'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '4.90'
        # item['FixedInterestRate_RateofinterestPA'] = '2.52'
        # item['ExcessMilageCharge'] = '9'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/12/2021'
        # item['RetailCashPrice'] = '18650.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/vehicles/2020/stonic/Stonic_Nav_240x135.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item

        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "ProCeed 'GT-Line' 1.5 Turbocharged Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "344.48"
        item['CustomerDeposit'] = "2584.00"
        item['RetailerDepositContribution'] = '2250.00'
        item['OnTheRoadPrice'] = '25840.00'
        item['AmountofCredit'] = '21006.00'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '12036.50'
        item['TotalAmountPayable'] = '29271.78'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '25840.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/stonic.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item

        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "XCeed '2' 1.0 Turbocharged Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "273.64"
        item['CustomerDeposit'] = "2126.50"
        item['RetailerDepositContribution'] = '2500.00'
        item['OnTheRoadPrice'] = '21265.00'
        item['AmountofCredit'] = '16638.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '9502.50'
        item['TotalAmountPayable'] = '23980.04'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '21265.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/stonic.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "e-Niro '2' Mid Range EV Automatic"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "545.97"
        # item['CustomerDeposit'] = "3289.50"
        # item['RetailerDepositContribution'] = 'N/A'
        # item['OnTheRoadPrice'] = '32895.00'
        # item['AmountofCredit'] = '29605.50'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '13832.00'
        # item['TotalAmountPayable'] = '36776.42'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '5.90'
        # item['FixedInterestRate_RateofinterestPA'] = '3.04'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/03/2022'
        # item['RetailCashPrice'] = '32895.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/stonic.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item


        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "Soul EV 'Maxx' Long Range EV Automatic"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "518.97"
        item['CustomerDeposit'] = "3499.50"
        item['RetailerDepositContribution'] = '1000.00'
        item['OnTheRoadPrice'] = '34995.00'
        item['AmountofCredit'] = '30495.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '16719.88'
        item['TotalAmountPayable'] = '39902.30'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '34995.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/stonic.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item

        item = CarItem()    ##  New
        item['CarMake'] = carMake
        item['CarModel'] = "Stinger 'GT S' 3.3 Turbocharged Petrol Automatic"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "739.04"
        item['CustomerDeposit'] = "4416.00"
        item['RetailerDepositContribution'] = '2250.00'
        item['OnTheRoadPrice'] = '44160.00'
        item['AmountofCredit'] = '37494.00'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '16521.30'
        item['TotalAmountPayable'] = '49792.74'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '44160.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/stonic.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


        item = CarItem()    ##  New
        item['CarMake'] = carMake
        item['CarModel'] = "Stonic '2' 1.0 Turbocharged Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "251.18"
        item['CustomerDeposit'] = "1926.00"
        item['RetailerDepositContribution'] = '1500.00'
        item['OnTheRoadPrice'] = '19260.00'
        item['AmountofCredit'] = '15834.00'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '9412.00'
        item['TotalAmountPayable'] = '21880.48'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '19260.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/stonic.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


        item = CarItem()    ##  New
        item['CarMake'] = carMake
        item['CarModel'] = "Sorento '2' 1.6 Turbocharged Petrol Self Charging Hybrid Automatic All Wheel Drive 7-seat"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "589.20"
        item['CustomerDeposit'] = "4059.00"
        item['RetailerDepositContribution'] = '750.00'
        item['OnTheRoadPrice'] = '40590.00'
        item['AmountofCredit'] = '35781.00'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '20405.55'
        item['TotalAmountPayable'] = '46425.75'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '40590.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/stonic.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item

        item = CarItem()    ##  New
        item['CarMake'] = carMake
        item['CarModel'] = "The all-new Sportage '2' 1.6 Turbocharged Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "331.66"
        item['CustomerDeposit'] = "2677.50"
        item['RetailerDepositContribution'] = '500.00'
        item['OnTheRoadPrice'] = '26775.00'
        item['AmountofCredit'] = '23597.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '14483.40'
        item['TotalAmountPayable'] = '29600.66'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '4.90'
        item['FixedInterestRate_RateofinterestPA'] = '2.52'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '26775.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/stonic.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item

        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "Optima Sportswagon '2' 1.6 CRDi ISG"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "383.24"
        # item['CustomerDeposit'] = "2345.5"
        # item['RetailerDepositContribution'] = '2500.00'
        # item['OnTheRoadPrice'] = '23455.00'
        # item['AmountofCredit'] = '18609.50'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '7117.50'
        # item['TotalAmountPayable'] = '25759.64'
        # item['OptionToPurchase_PurchaseActivationFee'] = ''
        # item['RepresentativeAPR'] = '5.9'
        # item['FixedInterestRate_RateofinterestPA'] = '3.04'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/12/2021'
        # item['RetailCashPrice'] = '23455.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/sportage.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item


        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "Sportage '3' 1.6 Diesel 48V Mild Hybrid Automatic DCT"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "427.17"
        # item['CustomerDeposit'] = "3097.00"
        # item['RetailerDepositContribution'] = '2500.00'
        # item['OnTheRoadPrice'] = '30970.00'
        # item['AmountofCredit'] = '25373.00'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '12836.40'
        # item['TotalAmountPayable'] = '33811.52'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '4.90'
        # item['FixedInterestRate_RateofinterestPA'] = '2.52'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/03/2022'
        # item['RetailCashPrice'] = '30970.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/kia3Assets/img/financeCalculator/sportage.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item

        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "The new Picanto 'GT-Line' 1.0 Petrol Automatic (4 Seat)"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "224.35"
        # item['CustomerDeposit'] = "1452.00"
        # item['RetailerDepositContribution'] = '1000.00'
        # item['OnTheRoadPrice'] = '14520.00'
        # item['AmountofCredit'] = '12068.00'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '5283.60'
        # item['TotalAmountPayable'] = '15812.20'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '4.90'
        # item['FixedInterestRate_RateofinterestPA'] = '2.52'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/12/2021'
        # item['RetailCashPrice'] = '14520.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/360vr/picanto_2017/kia-picanto_2017-2-midnight-black_0000.png.transform/trimimagethumbnail/img.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item

        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "The new Stinger 'GT S' 3.3 Turbocharged Petrol Automatic"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "651.50"
        # item['CustomerDeposit'] = '4290.50'
        # item['RetailerDepositContribution'] = '2500.00'
        # item['OnTheRoadPrice'] = '42905.00'
        # item['AmountofCredit'] = '36114.50'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '16583.40'
        # item['TotalAmountPayable'] = '46827.90'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '4.90'
        # item['FixedInterestRate_RateofinterestPA'] = '2.52'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/12/2021'
        # item['RetailCashPrice'] = '42905.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/static/new_cars_navigation_2019/Stinger_Nav_240x135.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item

        ###########################################################################

        # item = CarItem()
        # item['CarMake'] = carMake
        # item['CarModel'] = "The Kia EV6 'EV6' 77.4kWh lithium-ion RWD EV Automatic"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = "604.88"
        # item['CustomerDeposit'] = '4089.50'
        # item['RetailerDepositContribution'] = 'N/A'
        # item['OnTheRoadPrice'] = '40895.00'
        # item['AmountofCredit'] = '36805.50'
        # item['DurationofAgreement'] = '37'
        # item['OptionalPurchase_FinalPayment'] = '19192.50'
        # item['TotalAmountPayable'] = '45057.68'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '4.90'
        # item['FixedInterestRate_RateofinterestPA'] = '2.52'
        # item['ExcessMilageCharge'] = '9.0'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/12/2021'
        # item['RetailCashPrice'] = '40895.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/static/new_cars_navigation_2019/Stinger_Nav_240x135.png'
        # item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        # item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        # yield item


        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "The Kia EV6 'Air' 77.4kWh lithium-ion RWD EV Automatic"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "634.43"
        item['CustomerDeposit'] = '4169.50'
        item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = '41695.00'
        item['AmountofCredit'] = '37525.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '20740.80'
        item['TotalAmountPayable'] = '47749.78'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '41695.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/static/new_cars_navigation_2019/Stinger_Nav_240x135.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "XCeed Plug-In Hybrid '3' 1.6 Petrol Plug-in Hybrid Automatic DCT"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "496.96"
        item['CustomerDeposit'] = '3185.50'
        item['RetailerDepositContribution'] = '2500.00'
        item['OnTheRoadPrice'] = '31855.00'
        item['AmountofCredit'] = '26169.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '12285.38'
        item['TotalAmountPayable'] = '35861.44'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '31855.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/static/new_cars_navigation_2019/Stinger_Nav_240x135.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


        item = CarItem()
        item['CarMake'] = carMake
        item['CarModel'] = "Sorento Plug-In Hybrid '2' 1.6 Turbocharged Petrol Plug-In Hybrid Automatic All Wheel Drive 7 Seat"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = "730.48"
        item['CustomerDeposit'] = '4644.50'
        item['RetailerDepositContribution'] = '750.00'
        item['OnTheRoadPrice'] = '46445.00'
        item['AmountofCredit'] = '41050.50'
        item['DurationofAgreement'] = '37'
        item['OptionalPurchase_FinalPayment'] = '21232.50'
        item['TotalAmountPayable'] = '52924.28'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.90'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '46445.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/finance-calculator/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/static/new_cars_navigation_2019/Stinger_Nav_240x135.png'
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        yield item


    #################### HERE
    ####################### LEAD OFFER BEGINS


    
    ##############################################          30 SEP 2021         ###############################################################
        #1
        item = CarItem()
        item['CarMake'] = 'Kia'
        item['CarModel'] = "Picanto 'GT-Line S' 1.0 Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = '333.26'
        item['CustomerDeposit'] = '0.00'
        item['RetailerDepositContribution'] = '750.00'
        item['OnTheRoadPrice'] = '17155.00'
        item['AmountofCredit'] = '16405.00'
        item['DurationofAgreement'] = '24'
        item['OptionalPurchase_FinalPayment'] = '6832.75'
        item['TotalAmountPayable'] = '19,580.11'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.9'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '17155.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/offers/picanto-offers/personal-contract-purchase/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/newoffers/pcp/Picanto_PCP_1929x846.jpg'
        item['FinalPaymentPercent'] = 'N/A'
        item['DepositPercent'] = 'N/A'
        yield item

        #2
        item = CarItem()
        item['CarMake'] = 'Kia'
        item['CarModel'] = "XCeed '3' 1.5 Turbocharged Petrol Manual"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = '436.10'
        item['CustomerDeposit'] = '0.00'
        item['RetailerDepositContribution'] = '2500.00'
        item['OnTheRoadPrice'] = '25345.00'
        item['AmountofCredit'] = '22845.00'
        item['DurationofAgreement'] = '24'
        item['OptionalPurchase_FinalPayment'] = '10633.75'
        item['TotalAmountPayable'] = '28833.35'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '6.9'
        item['FixedInterestRate_RateofinterestPA'] = '3.55'
        item['ExcessMilageCharge'] = '9.0'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '25345.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/xceed/xceed-offers/personal-contract-purchase/'
        item['CarimageURL'] = '	https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/newoffers/pcp/xCeed_PCP_1929x846.jpg'
        item['FinalPaymentPercent'] = 'N/A'
        item['DepositPercent'] = 'N/A'
        yield item

        #3
        # item = CarItem()
        # item['CarMake'] = 'Kia'
        # item['CarModel'] = "Niro '3' 1.6 Petrol Self Charging Hybrid Automatic DCT"
        # item['TypeofFinance'] = "Personal Contract Purchase"
        # item['MonthlyPayment'] = '406.96'
        # item['CustomerDeposit'] = '5800.00'
        # item['RetailerDepositContribution'] = 'N/A'
        # item['OnTheRoadPrice'] = '28580.00'
        # item['AmountofCredit'] = '22780.00'
        # item['DurationofAgreement'] = '24'
        # item['OptionalPurchase_FinalPayment'] = '13013.00'
        # item['TotalAmountPayable'] = '28580.00'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = '0'
        # item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        # item['ExcessMilageCharge'] = '9'
        # item['AverageMilesPerYear'] = '10000'
        # item['OfferExpiryDate'] = '31/03/2022'
        # item['RetailCashPrice'] = '28580.00'
        # item['DebugMode'] = self.Debug_Mode
        # item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/offers/niro-offers/personal-contract-purchase/'
        # item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/2020_Offers/niro_hev/Niro_HEV_0percent_480x254.jpg'
        # item['FinalPaymentPercent'] = 'N/A'
        # item['DepositPercent'] = 'N/A'
        # yield item

        #4
        item = CarItem()
        item['CarMake'] = 'Kia'
        item['CarModel'] = "The all-new Sportage 'GT-Line S' 1.6 Turbocharged Petrol Hybrid Auto"
        item['TypeofFinance'] = "Personal Contract Purchase"
        item['MonthlyPayment'] = '346.48'
        item['CustomerDeposit'] = '9700.00'
        item['RetailerDepositContribution'] = '500.00'
        item['OnTheRoadPrice'] = '38655.00'
        item['AmountofCredit'] = '28455.00'
        item['DurationofAgreement'] = '24'
        item['OptionalPurchase_FinalPayment'] = '19526.30'
        item['TotalAmountPayable'] = '42210.38'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = '4.9'
        item['FixedInterestRate_RateofinterestPA'] = '2.52'
        item['ExcessMilageCharge'] = '9'
        item['AverageMilesPerYear'] = '10000'
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = '38655.00'
        item['DebugMode'] = self.Debug_Mode
        item['WebpageURL'] = 'https://www.kia.com/uk/new-cars/offers/sportage-offers/personal-contract-purchase/'
        item['CarimageURL'] = 'https://www.kia.com/content/dam/kwcms/kme/uk/en/assets/newoffers/pcp/Sportage_PCP_1929x846.jpg'
        item['FinalPaymentPercent'] = 'N/A'
        item['DepositPercent'] = 'N/A'
        yield item
