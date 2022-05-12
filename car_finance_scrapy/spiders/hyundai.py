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
from urllib.parse import urljoin
from html.parser import HTMLParser
from requests import Session

class HyundaiSpider(BaseSpider):
    name = "hyundai.co.uk"
    unique_data = set()
    allowed_domains = ['hyundai.co.uk', 'hyundaiconfigcalculator.co.uk']

    start_url = ['https://configure.hyundai.co.uk/middleware/api/models', 'https://www.hyundai.co.uk/offers/fleet', 'https://www.hyundai.co.uk/offers/finance-type/pch']
    def __init__(self):
        super(HyundaiSpider, self).__init__()

    def start_requests(self):
        for url  in self.start_url:
            # if "fleet" in url:
            #     yield Request(url, callback=self.parse_bch_link, headers=self.headers)
            # elif "finance-type/pch" in url:
            #     yield Request(url, callback=self.parse_pch_link, headers=self.headers)
            # else:
            if "/middleware/api/model" in url: 
                yield Request(url, callback=self.parse_model_url, headers=self.headers)

    def parse_bch_link(self, response): #### Contract hire
        link  = self.getTexts(response, "//a[contains(text(), 'See all')]/@href")
        for a in link:
            url = urljoin(response.url ,a)
            href = url + '/' + 'fleet'
            # print("href", href)
            # input("stop")
            yield Request(href, callback=self.parse_ch_items, headers=self.headers)

    def parse_pch_link(self, response): #### Contract hire
        link  = self.getTexts(response, "//a[contains(text(), 'See all')]/@href")
        for a in link:
            url = urljoin(response.url ,a)
            href = url + '/' + 'pch'
            # print("href", href)
            # input("stop")
            yield Request(href, callback=self.parse_ch_items, headers=self.headers)


    def parse_ch_items(self, response):
        ### IF One car on Page

        offer_text = self.getText(response, '//a[@class="car-tile__terms-button js-terms-button"]/@data-terms')
        if offer_text:
            offerExp = offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
            OfferExpiryDate = self.dateMatcher(offerExp)[1]
            DurationAgreement = offer_text.split("followed by ")[1].split(" monthly")[0]
            AverageMilesPerYear = offer_text.split("mileage of ")[1].split(" miles")[0]
        else:
            offer_text_bus = self.getText(response, '//div[@class="hero__terms"]/text()')
            if offer_text_bus:
                offerExp = offer_text_bus.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
                OfferExpiryDate = self.dateMatcher(offerExp)[1]
                DurationAgreement = offer_text_bus.split("followed by ")[1].split(" monthly")[0]
                AverageMilesPerYear = 'N/A'

        # if "tucson" in response.url or "i10" in response.url:
        if "/kona-electric/fleet" not in response.url:
            car_model = self.getText(response, '//h4[@class="car-tile__title car-tile__title--left car-tile__title--bottom car-tile__title--spaced"]/text()')
            image = self.getText(response, '//div[@class="car-tile__image car-tile__image--two-cols"]/@style')
            carImg = image.split("(")[1].split(")")[0]
            carImageURL = urljoin(response.url, carImg)
            data_text = self.getText(response, '//p[@class="car-tile__apr car-tile__apr--auto"]/text()')
            # monthly_customer_prices = re.findall(r'(?<!\d\.)\b\d+(?:,\d+)?\b(?!\.\d)', data_text)
            if "(exc VAT) per month, " in data_text:
                monthly_customer_prices = data_text.split("(exc VAT) per month, ")
            else:
                monthly_customer_prices = data_text.split("(inc VAT) per month, ")

            MonthlyPayment = self.remove_gbp(monthly_customer_prices[0])
            if " (exc VAT)" in monthly_customer_prices[1]:
                CustomerDeposit = self.remove_gbp(monthly_customer_prices[1].split(" (exc VAT)")[0]) ### BCH
            else:
                CustomerDeposit = self.remove_gbp(monthly_customer_prices[1].split("(inc VAT) initial rental")[0]) ### PCH
            ExcessMilageCharge = data_text.split("Hire, ")[1].split(" pence")[0]
            # print("url", response.url)
            # print("MonthlyPayment", MonthlyPayment)
            # print("CustomerDeposit", CustomerDeposit)
            # input("stop")
            if "pch" in response.url:
                TypeofFinance = 'Personal Contract Hire'
            elif "fleet" in response.url:
                TypeofFinance = 'Business Contract Hire'
            else:
                TypeofFinance = 'N/A'


            item = CarItem()
            item['CarMake'] = 'Hyundai'
            item['CarModel'] = self.remove_special_char_on_excel(car_model)
            item['TypeofFinance'] =  self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
            if item['MonthlyPayment']:
                item['MonthlyPayment'] = float(item['MonthlyPayment'])
            item['CustomerDeposit'] =  self.make_two_digit_no(CustomerDeposit)
            if item['CustomerDeposit']:
                item['CustomerDeposit'] = float(item['CustomerDeposit'])
            item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = DurationAgreement
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
            item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
            item['RetailCashPrice'] = 'N/A'
            item['OfferExpiryDate'] = OfferExpiryDate
            item['CarimageURL'] = carImageURL
            item['WebpageURL'] = response.url
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            # print("item", item)
            # print("resp", response.url)
            # input("stop")
            yield item

        # else: ### IF MORE THAN 1 CARS than
        if "/kona-electric/fleet" in response.url:
            path = response.xpath('//div[@class="car-grid__wrapper"]//div[@class="car-tile"]')
            for div in path:
                car_model = self.getText(div, './/h4[@class="car-tile__title car-tile__title--left car-tile__title--bottom car-tile__title--spaced"]/text()')
                image = self.getText(div, './/div[@class="car-tile__image car-tile__image--two-cols"]/@style')
                carImg = image.split("(")[1].split(")")[0]
                carImageURL = urljoin(response.url, carImg)

                data_text = self.getText(div, './/p[@class="car-tile__apr car-tile__apr--auto"]/text()')
                regex = r"[\$|€|£\20AC\00A3]{1}\d+(?:,\d+){0,2}"
                MonthlyPayment = re.search(regex, data_text).group()
                CustomerDeposit = data_text.split(", £")[1].split(" (exc")[0]
                ExcessMilageCharge = data_text.split("Hire, ")[1].split(" pence")[0]
                # print("mon : ", MonthlyPayment)
                # print("CustomerDeposit : ", carImageURL)
                # print("resp : ", response.url)
                # input("wait here 1:")
                item = CarItem()
                item['CarMake'] = 'Hyundai'
                item['CarModel'] = self.remove_special_char_on_excel(car_model)
                item['TypeofFinance'] =  self.get_type_of_finance('Business Contract Hire')
                item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
                if item['MonthlyPayment']:
                    item['MonthlyPayment'] = float(item['MonthlyPayment'])
                item['CustomerDeposit'] =  self.remove_gbp(CustomerDeposit)
                if item['CustomerDeposit']:
                    item['CustomerDeposit'] = float(item['CustomerDeposit'])
                item['RetailerDepositContribution'] = 'N/A'
                item['OnTheRoadPrice'] = 'N/A'
                item['OptionalPurchase_FinalPayment'] = 'N/A'
                item['AmountofCredit'] = 'N/A'
                item['DurationofAgreement'] = DurationAgreement
                item['TotalAmountPayable'] = 'N/A'
                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                item['RepresentativeAPR'] = 'N/A'
                item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                item['ExcessMilageCharge'] = ExcessMilageCharge
                item['AverageMilesPerYear'] = AverageMilesPerYear.replace(",", "")
                item['RetailCashPrice'] = 'N/A'
                item['OfferExpiryDate'] = OfferExpiryDate
                item['CarimageURL'] = carImageURL
                item['WebpageURL'] = response.url
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                yield item
    ############################ PCP AND Personal Motor Loan BELOW
    def parse_model_url(self, response):
        JO = json.loads(response.body)
        for data in JO:
            model_id = data['id']

            otrprice = data['minimum_configuration_price']
            parse_url = "https://configure.hyundai.co.uk/middleware/api/trims/"+str(model_id)
            model_name = data['name']
            # print("response: ", response.url)
            # print("model_name: ", model_name)
            # print("parse_url: ", parse_url)
            # input("stop")
            yield Request(parse_url, callback=self.parse_model, headers=self.headers, meta={"otrprice":otrprice, "model_name": model_name, "model_id": model_id})


    def parse_model(self, response): #### PCP AND HIRE PURECHASE
        otrprice = response.meta['otrprice']
        model_name = response.meta['model_name']
        model_id = response.meta['model_id']
        JO = json.loads(response.body)
        for data in JO:
            varient_id = data['id']
            varient_name = data['name']
            url = "https://configure.hyundai.co.uk/middleware/api/search/"+str(model_id)+"/"+str(varient_id)
            # print("response: ", response.url)
            # print("model_name: ", model_name)
            # # print("model_id: ", model_id)
            # print("varient_name: ", varient_name)
            # print("url: ", url)
            # input("stop")
            yield Request(url, callback=self.parse_model_next_url, headers=self.headers, meta={"otrprice":otrprice, "model_name": model_name, "model_id": model_id, "varient_name": varient_name, "varient_id": varient_id})

    def parse_model_next_url(self, response):
        otrprice = response.meta['otrprice']
        model_name = response.meta['model_name']
        model_id = response.meta['model_id']
        varient_name = response.meta['varient_name']
        varient_id = response.meta['varient_id']
        JO = json.loads(response.body)
        image = JO['image']
        cap_code = JO['cap_code']
        engine = JO['engine']['name']
        # if "HYSA22PRM5EDTM4 4" in cap_code:
        # print("url: ", response.url)
        # print("url: ", cap_code)
        # print("model_name: ", model_name)
        # print("varient_name: ", varient_name)
        # print("engine: ", engine)
        # input("wait here:")

        if "None" in str(cap_code):
            print("Not availble")
        else:
            price = JO['price']

            try:
                cap_code = cap_code.replace(" ", "%20")
            except Exception as e:
                print("Cap code error due to: ", e)
                print("JO: ", JO)
            import time    
            time.sleep(1)
            href = 'https://hyundai-configurator-stage.amaze.com/api/InitialPluginData/1/'+str(cap_code)+'/'+str(price)+'/0.00/?callback=jQuery31108214793964043248_1563880512946&_=1563880512948'

            # print("url: ", response.url)
            # print("url: ", cap_code)
            # print("model_name: ", model_name)
            # print("varient_name: ", varient_name)
            # print("price: ", price)
            # print("engine: ", engine)
            # print("href: ", href)
            # input("wait here:")

            yield Request(href, callback=self.parse_car_items, headers=self.headers, meta={"price":price, "model_name": model_name, "model_id": model_id, "varient_name": varient_name, "varient_id": varient_id, "image": image, "cap_code":cap_code, "engine":engine}, dont_filter=True)


    def parse_car_items(self, response):
        otrprice = response.meta['price']
        model_name = response.meta['model_name']
        model_id = response.meta['model_id']
        varient_name = response.meta['varient_name']
        varient_id = response.meta['varient_id']
        image = response.meta['image']
        cap_code = response.meta['cap_code']
        engine = response.meta['engine']
        # if "HYSA22PRM5EDTM4%204" in cap_code:
        #     print("model_name: ", model_name)
        #     print("varient_name: ", varient_name)
        #     print("engine: ", engine)
        #     print("cap_code: ", cap_code)
        #     input("wait here:")

        OfferExpiryDate = str()
        data = str(response.body)
        data = data.split("({")[1]
        data = data.split(");")[0]
        data = "{"+data
        data = data.replace('\r\n', '')
        data = data.replace(r'\x3E', '\x3E')
        data = data.replace(r'\x80', '\x80')
        data = data.replace(r'\xe2', '\xe2')
        data = data.replace(r'\x99', '\x99')
        data = json.loads(data)

        # print("url: ", response.url)
        # print("data : ", data)
        # print("model_name: ", model_name)
        # print("varient_name: ", varient_name)
        # print("engine: ", engine)
        # print("cap_code: ", cap_code)
        # input("wait here:")
        #### PCP DATA

        # model_name_ = model_name +' '+varient_name+' '+engine
        # if "i30 Premium SE 1.4 140PS Petrol 2WD Manual" in model_name_:
        #
        #     print("Data: ", data['PluginProducts'])
        #     print("model_name: ", model_name_)
        #     # print("varient_name: ", varient_name)
        #     # print("engine: ", engine)
        #     input("Wait here:")

        # print("data: ", data)
        # input("wait here:")

        for PCP_Product_data in data['PluginProducts']:
            
            ProductName = PCP_Product_data['ProductName'] ###  Hyundai PCP P3 5.4% APR
            # if "PCP" in ProductName and "4.6% APR" in ProductName or "0% APR" in ProductName or "Personal Contract Purchase APR - Cars - 7.9" in ProductName:
            if "Hyundai PCP - " in ProductName:
                FinancePeriodData = PCP_Product_data['FinancePeriodData']
                for finance in FinancePeriodData['FinancePeriods']:
                    period = finance['Period']
                    url = 'https://hyundaiconfigcalculator.co.uk/api/QuotePluginData/1/'+str(cap_code)+'/'+str(otrprice)+'/0.00/pcp/'+str(period)+'/10000/2400/null/null/?callback=jQuery31107691658387674154_1625565732173&_=1625565732178'
                    # url = 'https://hyundai-configurator-stage.amaze.com/api/QuotePluginData/1/'+str(cap_code)+'/'+str(otrprice)+'/0.00/pcp/'+str(period)+'/10000/2400/null/null/?callback=jQuery31108214793964043248_1563880512946&_=1563880512953'
                    # print("period: ", url)
                    # input("wait here:")
                    yield Request(url, callback=self.parse_pcp_car_item, headers=self.headers, meta={"otrprice":otrprice, "model_name": model_name, "model_id": model_id, "varient_name": varient_name, "varient_id": varient_id, "image": image, "cap_code":cap_code, "engine":engine}, dont_filter=True)

            # elif "PML" in ProductName and "4.6% APR" in ProductName or "0% APR" in ProductName or "Standard APR - Cars - 7.9" in ProductName:
            elif 'Hyundai PML - ' in ProductName:

                ###    Hyundai PML - P3 5.4% APR
                FinancePeriodData = PCP_Product_data['FinancePeriodData']
                for finance in FinancePeriodData['FinancePeriods']:
                    period = finance['Period']
                    if "24" in str(period) or "30" in str(period) or "36" in str(period) or "42" in str(period) or "48" in str(period):
                        url = 'https://hyundaiconfigcalculator.co.uk/api/QuotePluginData/1/'+str(cap_code)+'/'+str(otrprice)+'/0.00/cs/'+str(period)+'/0/1800/null/30/?callback=jQuery31107691658387674154_1625565732173&_=1625565732186'
                        # url = 'https://hyundaiconfigcalculator.co.uk/api/QuotePluginData/1/'+str(cap_code)+'/'+str(otrprice)+'/0.00/cs/'+str(period)+'/0/1800/null/null/?callback=jQuery31108214793964043248_1563880512946&_=1563880512957'
                        yield Request(url, callback=self.parse_cs_car_item, headers=self.headers, meta={"otrprice":otrprice, "model_name": model_name, "model_id": model_id, "varient_name": varient_name, "varient_id": varient_id, "image": image, "cap_code":cap_code, "engine":engine}, dont_filter=True)

    def parse_pcp_car_item(self, response):
        """PCP OFFER
        """
        otrprice = response.meta['otrprice']
        model_name = response.meta['model_name']
        model_id = response.meta['model_id']
        varient_name = response.meta['varient_name']
        varient_id = response.meta['varient_id']
        image = response.meta['image']
        cap_code = response.meta['cap_code']
        CarEngine = response.meta['engine']
        varient_name_url = varient_name.lower()
        varient_name_url = varient_name_url.replace(" ", "-")
        model_name_url = model_name.lower()
        if " " in model_name_url:
            model_name_url = model_name_url.replace(" ", "-")
        href_back = "http://configure.hyundai.co.uk/build/"+str(model_name_url)
        data = str(response.body)
        data = data.split("({")[1]
        data = data.split(");")[0]
        data = "{"+data
        data = data.replace('\r\n', '')
        data = data.replace(r'\x3E', '')
        data = data.replace(r'\x80', '')
        data = data.replace(r'\xe2', '')
        data = data.replace(r'\x99', '')

        # data = json.loads(data)
        # print("url: ", response.url)
        # print("data: ", data)
        # print("type: ", type(data))
        # input("stop")
        try:
            data = json.loads(data)
        except Exception as e:
            data = data.replace(r'\x3E', '')
            data = data.replace(r'\x80', '')
            data = data.replace(r'\xe2', '')
            data = data.replace(r'\x99', '')
            data = json.loads(data)

        # print("data: ", data)
        # input("wait here11:")

        MonthlyPayment = data['MonthlyPayment']
        CustomerDeposit = data['CustomerDeposit']
        OnRoadPrice = data['OnRoadPrice']
        AmountOfCredit = data['AmountOfCredit']
        FixedRateInterest = data['FixedRateInterest']
        DurationAgreement = data['DurationAgreement']
        AnnualMileage = data['AnnualMileage']
        ExcessMileageCharge = data['ExcessMileageCharge']
        TotalAmountPayable = data['TotalAmount']
        APR = data['APR']
        DepositContribution = data['DepositContribution']
        OptionalPurchase_FinalPayment = data['FinalPayment']
        TermsConditionsParagraphs = data['TermsConditionsParagraphs'][0]
        find_date = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", TermsConditionsParagraphs)
        for date in find_date:
            OfferExpiryDate = date
        TypeofFinance = 'PCP'
        item = CarItem()
        item['CarMake'] = 'Hyundai'
        item['CarModel'] = self.remove_special_char_on_excel(model_name +" "+ varient_name +" "+ CarEngine)
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
        if item['MonthlyPayment']:
            item['MonthlyPayment'] = float(item['MonthlyPayment'])
        item['CustomerDeposit'] =  CustomerDeposit
        if item['CustomerDeposit']:
            item['CustomerDeposit'] = float(item['CustomerDeposit'])
        item['RetailerDepositContribution'] = DepositContribution
        if item['RetailerDepositContribution']:
            item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
        item['OnTheRoadPrice'] = OnRoadPrice
        if item['OnTheRoadPrice']:
            item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
        item['OptionalPurchase_FinalPayment'] = OptionalPurchase_FinalPayment
        item['AmountofCredit'] = AmountOfCredit
        item['DurationofAgreement'] = DurationAgreement
        item['TotalAmountPayable'] = TotalAmountPayable
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = APR
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(str(FixedRateInterest))
        item['ExcessMilageCharge'] = self.remove_percentage_sign(str(ExcessMileageCharge))
        item['AverageMilesPerYear'] = self.remove_percentage_sign(str(AnnualMileage))
        item['RetailCashPrice'] = OnRoadPrice
        item['OfferExpiryDate'] = OfferExpiryDate
        item['CarimageURL'] = image
        item['WebpageURL'] = href_back
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        yield item


    def parse_cs_car_item(self, response):
        """PML PERSONAL MOTOR LOAN ->HP
        """
        otrprice = response.meta['otrprice']
        model_name = response.meta['model_name']
        model_id = response.meta['model_id']
        varient_name = response.meta['varient_name']
        varient_id = response.meta['varient_id']
        image = response.meta['image']
        cap_code = response.meta['cap_code']
        CarEngine = response.meta['engine']

        varient_name_url = varient_name.lower()
        varient_name_url = varient_name_url.replace(" ", "-")
        model_name_url = model_name.lower()
        if " " in model_name_url:
            model_name_url = model_name_url.replace(" ", "-")
        href_back = "http://configure.hyundai.co.uk/build/"+str(model_name_url)
        data = str(response.body)
        data = data.split("({")[1]
        data = data.split(");")[0]
        data = "{"+data
        data = data.replace('\r\n', '')
        data = data.replace(r'\x3E', '')
        data = data.replace(r'\x80', '')
        data = data.replace(r'\xe2', '')
        data = data.replace(r'\x99', '')

        # data = json.loads(data)
        # print("url: ", response.url)
        # print("data: ", data)
        # print("type: ", type(data))
        # input("stop")
        try:
            data = json.loads(data)
        except Exception as e:
            data = data.replace(r'\x3E', '')
            data = data.replace(r'\x80', '')
            data = data.replace(r'\xe2', '')
            data = data.replace(r'\x99', '')
            data = json.loads(data)

        # print("data: ", data)
        # print("type: ", response.url)
        # input("stop")

        MonthlyPayment = data['MonthlyPayment']
        CustomerDeposit = data['CustomerDeposit']
        OnRoadPrice = data['OnRoadPrice']
        AmountOfCredit = data['AmountOfCredit']
        FixedRateInterest = data['FixedRateInterest']
        DurationAgreement = data['DurationAgreement']
        AnnualMileage = data['AnnualMileage']
        ExcessMileageCharge = data['ExcessMileageCharge']
        TotalAmountPayable = data['TotalAmount']
        APR = data['APR']
        DepositContribution = data['DepositContribution']
        OptionalPurchase_FinalPayment = data['FinalPayment'] ### OPT FINAL PAYMENT
        TermsConditionsParagraphs = data['TermsConditionsParagraphs'][0]
        find_date = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", TermsConditionsParagraphs)
        for date in find_date:
            OfferExpiryDate = date
        TypeofFinance = 'Hire Purchase' ### == Contract Hire

        item = CarItem()
        item['CarMake'] = 'Hyundai'
        item['CarModel'] = self.remove_special_char_on_excel(model_name +" "+ varient_name +" "+ CarEngine)
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
        if item['MonthlyPayment']:
            item['MonthlyPayment'] = float(item['MonthlyPayment'])
        item['CustomerDeposit'] =  CustomerDeposit
        if item['CustomerDeposit']:
            item['CustomerDeposit'] = float(item['CustomerDeposit'])
        item['RetailerDepositContribution'] = DepositContribution
        if item['RetailerDepositContribution']:
            item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
        item['OnTheRoadPrice'] = OnRoadPrice
        if item['OnTheRoadPrice']:
            item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
        item['OptionalPurchase_FinalPayment'] = 'N/A'
        item['AmountofCredit'] = AmountOfCredit
        item['DurationofAgreement'] = DurationAgreement
        item['TotalAmountPayable'] = TotalAmountPayable
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = APR
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(str(FixedRateInterest))
        item['ExcessMilageCharge'] = self.remove_percentage_sign(str(ExcessMileageCharge))
        # item['AverageMilesPerYear'] = AnnualMileage
        item['AverageMilesPerYear'] = 'N/A'
        item['RetailCashPrice'] = OnRoadPrice
        item['OfferExpiryDate'] = OfferExpiryDate
        item['CarimageURL'] = image
        item['WebpageURL'] = href_back
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        yield item
