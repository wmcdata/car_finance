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
import requests
from urllib.parse import urljoin
from html.parser import HTMLParser
from requests import Session
import requests
### PCP Cars
### CONTRACT HIRE Cars
### VANS All

class CitroenSpider(BaseSpider):
    name = "citroen.co.uk"

    allowed_domains = ['citroen.co.uk', 'codeweavers.net', 'info.citroen.co.uk']
    base_url  = 'https://info.citroen.co.uk'
    start_url = ['https://store.citroen.co.uk/configurable/finance/', 'https://www.citroen.co.uk/offers/new-car-offers/personal-lease', 'https://info.citroen.co.uk/offers/car/business', 'https://info.citroen.co.uk/offers/van', 'https://www.citroen.co.uk/buy/finance-calculator.html']
    ### Car both PCP and BCH

    def __init__(self):
        super(CitroenSpider, self).__init__()

    def start_requests(self):
        for url in self.start_url:
            # if "business" in url:
            #     yield Request(url, callback=self.parse_business_cars, headers=self.headers)
            if "offers/van" in url:
                yield Request(url, callback=self.parse_vans, headers=self.headers)
            elif "personal-lease" in url:
                yield Request(url, callback=self.parse_lease_offers_link, headers=self.headers)
            # elif "/car-finance-part-exchange-calculator/" in url:
            #     yield Request(url, callback=self.parse_pcp_calculator, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_car, headers=self.headers)

    def parse_car(self, response):
        # print("url: ", url)
        # response.xpath('//div[@class="pcpVehiclesGrid representative-models-wrapper"]/div[@class="row"]/representative-model').extract()
        link = response.xpath('//div[contains(@class, "OfferGridStyled")]//div[@class="carTitleWrap"]')
        for a in link:
            href = self.getText(a, "./a/@href")
            url = response.urljoin(href)
            # print("url: ", url)
            # input("stop")
            yield Request(url, callback=self.parse_pcp_offers_data_url, headers=self.headers)


    def parse_lease_offers_link(self, response):
        """PERSONAL LEASE
        """
        link = response.xpath('//div[@class="offerVehContainer"]//div[@class="offerVehBloc"]')
        for a in link:
            href = self.getText(a, './/a[contains(text(), "Discover Offers")]/@href')
            url = response.urljoin(href)
            # print("url:", response.url)
            # print("url:", url)
            # input("stop")
            yield Request(url, callback=self.parse_personal_lease_offer_data, headers=self.headers, dont_filter=True)

    def parse_personal_lease_offer_data(self, response):
        """DATA COLLECT HERE PERSONAL LEASE
        """
        # print("url:", response.url)
        # input("stop")
        MonthlyPayment = self.remove_gbp(self.getText(response, '//p[@class="price"]/span/text()'))
        CarimageURL = self.getText(response, '//div/@data-original')

        dataText = self.getTextAll(response, '//p//strong[contains(text(), "participating dealers")]//text()')
        if dataText:
            carModel = dataText.split("month available on")[1].split(".")[0]
            CustomerDeposit = dataText.split("rental of ")[1].split("p")[0]
            DepositContribution = dataText.split("plus")[1].split(" Citro")[0]


            item = CarItem()
            item['CarMake'] = 'Citroen'
            item['CarModel'] = self.remove_special_char_on_excel(carModel)
            item['TypeofFinance'] = 'Personal Lease'
            item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
            if CustomerDeposit:
                item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
            else:
                item['CustomerDeposit'] = 'N/A'
            if DepositContribution:
                item['RetailerDepositContribution'] = self.remove_gbp(DepositContribution)
            else:
                item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['OptionalPurchase_FinalPayment'] =  'N/A'
            item['AmountofCredit'] =  'N/A'
            item['DurationofAgreement'] = '48'
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = 'N/A'
            item['RetailCashPrice'] =  'N/A'
            item['CarimageURL'] = 'N/A'
            item['WebpageURL'] = response.url
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            item['OfferExpiryDate'] = '30/06/2022'
            # termsUrl = 'https://www.citroen.co.uk/terms-and-conditions'
            # yield Request(termsUrl, callback=self.parse_for_expirydate_lease, headers=self.headers, dont_filter=True, meta={"item":item})
            # yield item

    # def parse_for_expirydate_lease(self, response):
    #     """Offer expiry date
    #     """
    #     item = response.meta['item']
    #     termsData = self.getTextAll(response, '//div[@class="zonetexte"]/p//text()')
    #     OfferExpiryDate = termsData.split("ordered and delivered between")[1].split("and")[0].split("-")[1].strip()
    #     # print("Engine_price", termsData)
    #     # input("stop")
    #     item['OfferExpiryDate'] = OfferExpiryDate.replace("/21", "/2021")
    #     yield item


    def parse_pcp_offers_data_url(self, response):
        """DATA PCP OFFERS
        """
        # print("resp: ", response.url)
        # input("sto")
        dataJson = self.getText(response, '//script[contains(text(), "TrimSelector")]/text()')
        dataJson = json.loads(dataJson)
        # print("dataJson",dataJson)
        # input("wait for dataJson")

        # Content = initialState['Content']['faq'][6]['content']
        # OfferExpiryDate = Content.split("to ")[1].split(" ")[0].replace("21", "2021")

        ####################################    05 October 2021 ####################################################
        initialState = dataJson['props']['initialState']
        try:
            Content = initialState['Content']['faq'][5]['content']
            OfferExpiryDate = Content.split("2021 to ")[1].split(".")[0].replace("th ", "/").replace("September ", "09/")
        except:
            OfferExpiryDate = "N/A"
        ########################################################################################
        # offerExp = Content.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "").replace("30", "30")
        # OfferExpiryDate = self.dateMatcher(Content)
        # print("resp: ", response.url)
        # print("dataJson: ", OfferExpiryDate)
        # input("sto")
        TrimSelector = initialState['TrimSelector']['configurable']
        trims = TrimSelector['trims']
        for trim_data in trims:
            trim_id = trim_data['_id']
            CarModel = trim_data['title']
            CarimageURL = trim_data['images'][0]['url']

            url = "https://store.citroen.co.uk/fc/api/v3/4/en/calculate-for-summary"

            payload = "{\"carConfigId\":\""+trim_id+"\"}"
            headers = {
                'content-type': "application/json",
                'cache-control': "no-cache",
                'postman-token': "438adbd2-0d5b-90ed-5d43-c542b58f8f35"
                }

            responses = requests.request("POST", url, data=payload, headers=headers)
            Offer_data = json.loads(responses.text)
            if Offer_data:
                blocks = Offer_data['blocks'][0]
                # print("trim_data: ", blocks)
                # input("sto")
                displayLines = blocks['displayLines']
                data = dict()
                for carOffers in displayLines:
                    label = carOffers['label']
                    value = carOffers['value']
                    data.update({label:value})
                OnTheRoadPrice = data['Citroën Store Price/Cash Price']
                if "47 Monthly Payments" in data:
                    MonthlyPayment = data['47 Monthly Payments']
                elif "36 Monthly Payments" in data:
                    MonthlyPayment = data['36 Monthly Payments']
                CustomerDeposit = data['Customer Deposit']
                DurationofAgreement = data['Term of Agreement']
                AmountOfCredit = data['Total Amount of Credit']
                TotalAmountPayable = data['Total Amount Payable']
                OptionalPurchase_FinalPayment = data['Optional Final Payment']
                FixedInterestRate_RateofinterestPA = data['Fixed Rate of Interest per Year']
                if "Representative APR" in data:
                    RepresentativeAPR = data['Representative APR']
                elif "APR Representative" in data:
                    RepresentativeAPR = data['APR Representative']    
                elif "APR" in data:
                    RepresentativeAPR = data['APR']
                else:
                    RepresentativeAPR = 'N/A'
                AverageMilesPerYear = data['Annual Mileage']
                ExcessMilageCharge = data['Excess Mileage Charge (pence per mile)']

                # print("Offer_data: ", data)
                # print("resp: ", response.url)
                # # # print("trim_id: ", trim_id)
                # # # print("title: ", title)
                # # print("trim_data: ", trim_data)
                # input("sto")


                item = CarItem()
                item['CarMake'] = 'Citroen'
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                item['TypeofFinance'] = 'Personal Contract Purchase'
                item['MonthlyPayment'] =  self.make_two_digit_no(MonthlyPayment)
                item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
                item['RetailerDepositContribution'] = ''
                item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
                item['OptionalPurchase_FinalPayment'] =  self.remove_gbp(OptionalPurchase_FinalPayment)
                item['AmountofCredit'] =  self.remove_gbp(AmountOfCredit)
                item['DurationofAgreement'] = DurationofAgreement
                item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
                item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice)
                item['CarimageURL'] = CarimageURL
                item['WebpageURL'] = response.url
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                item['OfferExpiryDate'] = OfferExpiryDate ### 31 March 2021
                # termsUrl = 'https://www.citroen.co.uk/terms-and-conditions'
                # yield Request(termsUrl, callback=self.parse_for_expirydate_main_offer, headers=self.headers, dont_filter=True, meta={"item":item})
                yield item

    # def parse_for_expirydate_main_offer(self, response):
    #     """Offer expiry date
    #     """
    #     item = response.meta['item']
    #     termsData = self.getTextAll(response, '//div[@class="zonetexte"]/p//text()')
    #     OfferExpiryDate = termsData.split("ordered and delivered between")[1].split("and")[0].split("-")[1].strip()
    #     # print("Engine_price", termsData)
    #     # input("stop")
    #     item['OfferExpiryDate'] = OfferExpiryDate.replace("/21", "/2021")
    #     yield item


    def parse_exact_link_data(self, response):

        financetype =self.getTexts(response, '//div[@id="fixthis"]//ul/li[contains(@class, "tabs__header__tab")]/text()')
        for type in financetype:
            # if "Personal Contract Purchase" in type:
            #     url = response.url
            #     # print("url: ", type)
            #     # print("url: ", response.url)
            #     # input("sto")
            #     yield Request(url, callback=self.parse_extract_pcp_data, headers=self.headers, dont_filter=True)
            if "Personal Contract Hire" in type:
                url = response.url + 'personal-contract-hire'
                yield Request(url, callback=self.parse_extract_contract_hire_data, headers=self.headers)
            elif "Personal Lease" in type:
                url = response.url + 'personal-lease'
                yield Request(url, callback=self.parse_exact_personal_lease_data, headers=self.headers)
            else:
                # print("url: ", type)
                print("url: ", response.url)
                # input("sto")


    def parse_extract_contract_hire_data(self, response):
        """DATA COLLECT HERE PCH
        """

        termsAndCondition = self.getTextAll(response,'//div[@class="terms-and-conditions"]//p[@class="small"]/text()')
        CarModel = termsAndCondition.split(" example based on ")[1].split(".")[0]
        CustomerDeposit = termsAndCondition.split("Initial customer rental ")[1].split(", ")[0]
        DurationofAgreement = termsAndCondition.split("followed by ")[1].split("m")[0]
        MonthlyPayment = termsAndCondition.split("monthly rentals of")[1].split("C")[0]
        AverageMilesPerYear = termsAndCondition.split("Examples based on")[1].split(" m")[0]

        # print("url: ", response.url)
        # print("CarModel: ", CarModel)
        # print("CustomerDeposit: ", CustomerDeposit)
        # print("DurationofAgreement: ", DurationofAgreement)
        # print("MonthlyPayment: ", MonthlyPayment)
        # print("AverageMilesPerYear: ", AverageMilesPerYear)
        # print("termsAndCondition: ", termsAndCondition)
        # input("sto")
        item = CarItem()
        item['CarMake'] = 'Citroen'
        item['CarModel'] = self.remove_special_char_on_excel(CarModel)
        item['TypeofFinance'] = 'Personal Contract Hire'
        item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
        item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
        item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = 'N/A'
        item['OptionalPurchase_FinalPayment'] =  'N/A'
        item['AmountofCredit'] = 'N/A'
        item['DurationofAgreement'] = DurationofAgreement
        item['TotalAmountPayable'] = 'N/A'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = 'N/A'
        item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        item['ExcessMilageCharge'] = 'N/A'
        item['AverageMilesPerYear'] = AverageMilesPerYear
        item['OfferExpiryDate'] = '30/06/2022'
        item['RetailCashPrice'] = 'N/A'
        item['CarimageURL'] = ''
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        yield item


    def parse_pcp_calculator(self, response):
        """PCP calculator DATA
        """

        url = "https://services.codeweavers.net/api/vehicleselection/datasets/PSAComCar/options"
        headers = {
            'accept': "application/json, text/plain, */*",
            'content-type': "application/json;charset=UTF-8",
            'origin': "https://plugins.codeweavers.net",
            'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            'x-cw-apikey': "Citroen-Y8K6DIv6VE17Bn4GP6",
            'x-cw-applicationname': "Plugin PSA",
            'cache-control': "no-cache",
            'postman-token': "b9213805-5c06-1f42-d2a1-9cb323885302"
        }

        payload = '{"PreviouslySelectedOptions":["Car","Citroen"],"AllowedManufacturers":[]}'

        response = requests.request("POST", url, data=payload, headers=headers)
        data = json.loads(response.text)
        Options = data['Options']
        for model in Options:
            modelName = model['Display'] ### Model NAME

            url = "https://services.codeweavers.net/api/vehicleselection/datasets/PSAComCar/options"
            payload = '{"PreviouslySelectedOptions":["Car","Citroen","'+modelName+'"],"AllowedManufacturers":[]}'
            headers = {
                'accept': "application/json, text/plain, */*",
                'content-type': "application/json;charset=UTF-8",
                'origin': "https://plugins.codeweavers.net",
                'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                'x-cw-apikey': "Citroen-Y8K6DIv6VE17Bn4GP6",
                'x-cw-applicationname': "Plugin PSA",
                'cache-control': "no-cache",
                'postman-token': "b9213805-5c06-1f42-d2a1-9cb323885302"
            }


            response = requests.request("POST", url, data=payload, headers=headers)
            Vardata = json.loads(response.text)

            VarOptions = Vardata['Options']
            for varient in VarOptions:
                var_type = varient['Display'] ### VARIETN NAME
                url = "https://services.codeweavers.net/api/vehicleselection/datasets/PSAComCar/options"

                payload = '{"PreviouslySelectedOptions":["Car","Citroen","'+modelName+'","'+var_type+'"],"AllowedManufacturers":[]}'
                headers = {
                    'accept': "application/json, text/plain, */*",
                    'content-type': "application/json;charset=UTF-8",
                    'origin': "https://plugins.codeweavers.net",
                    'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                    'x-cw-apikey': "Citroen-Y8K6DIv6VE17Bn4GP6",
                    'x-cw-applicationname': "Plugin PSA",
                    'cache-control': "no-cache",
                    'postman-token': "b9213805-5c06-1f42-d2a1-9cb323885302"
                }

                Der_response = requests.request("POST", url, data=payload, headers=headers)
                Derv_data = json.loads(Der_response.text)
                DerOptions = Derv_data['Options']

                for derivative in DerOptions:
                    der_type = derivative['Display'] ### Derivative NAME
                    der_code = derivative['Id'] ### Derivative CODE

                    url = "https://services.codeweavers.net/api/vehicleselection/datasets/PSAComCar/options"

                    payload = '{"PreviouslySelectedOptions":["Car","Citroen","'+modelName+'","'+var_type+'","'+der_code+'"],"AllowedManufacturers":[]}'
                    headers = {
                        'accept': "application/json, text/plain, */*",
                        'content-type': "application/json;charset=UTF-8",
                        'origin': "https://plugins.codeweavers.net",
                        'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
                        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                        'x-cw-apikey': "Citroen-Y8K6DIv6VE17Bn4GP6",
                        'x-cw-applicationname': "Plugin PSA",
                        'cache-control': "no-cache",
                        'postman-token': "b9213805-5c06-1f42-d2a1-9cb323885302"
                     }

                    veh_option = requests.request("POST", url, data=payload, headers=headers)
                    veh_data = json.loads(veh_option.text)
                    VehicleOptions = veh_data['Options']
                    for veh_opt in VehicleOptions:
                        Vehicle_type = veh_opt['Display'] ### Vehicle Option Name
                        Vehicle_Identifier = veh_opt['Id'] ### Vehicle Indentifier

                        carModel = modelName +' '+ var_type +' '+ der_type
                        url = 'https://services.codeweavers.net/public/v2/Vehicle/OptionsFor?Identifier='+Vehicle_Identifier+'&IdentifierType=Titre'
                        yield Request(url, callback=self.parse_pcp_model, headers=headers, dont_filter=True, meta={"Vehicle_Identifier":Vehicle_Identifier, "carModel":carModel})

    def parse_pcp_model(self, response):
        #########################
        ### PCP CARS ###
        #########################
        Vehicle_Identifier = response.meta['Vehicle_Identifier']
        carModel = response.meta['carModel']
        identifier_data = json.loads(response.body)
        Idf_Options = identifier_data['Options']
        for Idf_opt in Idf_Options:
            Engine_type = Idf_opt['Description'] ### Description Perla Nera Black metallic
            Engine_Code = Idf_opt['Id'] ### ID 0MM00N9V
            Engine_price = Idf_opt['Price'] ### PRICE 595.0
            carModels = carModel +" "+ Engine_type
            url = "https://services.codeweavers.net/api/finance/calculatefordisplay"

            payload = '{"Credentials":{"ApiKey":"Y8K6DIv6VE17Bn4GP6","SystemKey":"Citroen","Referrer":"https://info.citroen.co.uk/finance/car-finance-part-exchange-calculator/"},"VehicleRequests":[{"Id":"Finance Plugin","BuildToOrderVehicle":{"Identifier":"'+Vehicle_Identifier+'","Type":"car","SelectedOptions":[{"Code":"'+Engine_Code+'","Price":"'+str(Engine_price)+'"}]},"Parameters":{"DepositType":"Amount","RegularPayment":200,"IsTelematics":false,"AddTelematics":false,"CalculationType":"ToRegularPayment","CashDeposit":2000}}],"Customer":{}}'

            headers = {
                'accept': "application/json, text/plain, */*",
                'content-type': "application/json;charset=UTF-8",
                'origin': "https://plugins.codeweavers.net",
                'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                'x-cw-apikey': "Citroen-Y8K6DIv6VE17Bn4GP6",
                'x-cw-applicationname': "Plugin PSA",
                'cache-control': "no-cache",
                'postman-token': "b9213805-5c06-1f42-d2a1-9cb323885302"
             }

            car_Data = requests.request("POST", url, data=payload, headers=headers)
            full_data = json.loads(car_Data.text)

            Vehicles = full_data['Vehicles'][0]
            FinanceQuotations = Vehicles['FinanceQuotations'][0]
            # print("url", response.url)
            # # print("Vehicles", Vehicles)
            # input("stop")
            # TypeofFinance = FinanceQuotations['Finance']['Key']
            if "Blocks" in FinanceQuotations:
                if len(FinanceQuotations['Blocks']) > 0:
                    Quotes = FinanceQuotations['Blocks'][0]

                    data = dict()
                    DataQuotes = Quotes['Details']
                    for citroen_data in DataQuotes:
                        value = citroen_data['Value']
                        key = citroen_data['Key']
                        data.update({key:value})

                    OnTheRoadPrice = data['VehiclePrice']
                    AmountofCredit = data['AmountOfCredit']
                    MonthlyPayment = data['TotalRegularPayment']
                    CustomerDeposit = data['CustomerCashDeposit']
                    OptionalPurchase_FinalPayment = data['OptionalFinalPayment']
                    TotalAmountPayable = data['TotalAmountPayable']
                    DurationofAgreement = data['TermOfAgreement']
                    RepresentativeAPR = data['Apr']
                    FixedInterestRate_RateofinterestPA = data['FixedRateOfInterest']
                    if "MileagePerAnnum" in data:
                        AnnualMileage = data['MileagePerAnnum']
                    else:
                        AnnualMileage = 'N/A'
                    if "ManufacturerAndRetailerDepositContribution" in data:
                        RetailerDepositContribution = data['ManufacturerAndRetailerDepositContribution']
                    else:
                        RetailerDepositContribution = 'N/A'
                    if "ExcessMileageCharge" in data:
                        ExcessMileageRate = data['ExcessMileageCharge']
                    else:
                        ExcessMileageRate = 'N/A'


                    item = CarItem()
                    item['CarMake'] = 'Citroen'
                    item['CarModel'] = self.remove_special_char_on_excel(carModels)
                    item['TypeofFinance'] = self.get_type_of_finance('PCP')
                    item['MonthlyPayment'] = MonthlyPayment
                    item['CustomerDeposit'] = CustomerDeposit
                    item['RetailerDepositContribution'] = RetailerDepositContribution
                    item['OnTheRoadPrice'] = OnTheRoadPrice
                    item['OptionalPurchase_FinalPayment'] =  OptionalPurchase_FinalPayment
                    item['AmountofCredit'] =  AmountofCredit
                    item['DurationofAgreement'] = DurationofAgreement
                    item['TotalAmountPayable'] = TotalAmountPayable
                    item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                    item['RepresentativeAPR'] = RepresentativeAPR
                    item['FixedInterestRate_RateofinterestPA'] = FixedInterestRate_RateofinterestPA
                    item['ExcessMilageCharge'] = ExcessMileageRate
                    item['AverageMilesPerYear'] = AnnualMileage
                    item['OfferExpiryDate'] = 'N/A'
                    item['RetailCashPrice'] =  OnTheRoadPrice
                    item['CarimageURL'] = ''
                    item['WebpageURL'] = 'https://info.citroen.co.uk/finance/car-finance-part-exchange-calculator/'
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    try:
                        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    except:
                        item['DepositPercent'] = float()
                    yield item



    def parse_business_cars(self, response):

        link = response.xpath('//div[@class="offerVehContainer"]//div[@class="offerVehBloc"]')
        for a in link:
            href = self.getText(a, './/a[contains(text(), "Discover Offers")]/@href')
            url = response.urljoin(href)
            # print("url:", response.url)
            # print("url:", url)
            # input("stop")
            # if "car-range/citroen-c-zero" not in href and "car-range/citroen-spacetourer" not in href:
            #     if "new-cars" in url:
            #         links = url.replace("offers", "business-offers")
            yield Request(url, callback=self.parse_business_model, headers=self.headers)

    def parse_business_model(self, response):
        """BUSINESS Cars
        """
        carModelCheck = self.getText(response, '//h3[@class="offersTitle"]//text()')
        if " " in carModelCheck:
            carModelCheck1 = carModelCheck.split(" ")[0]
            carModelCheck2 = carModelCheck.split(" ")[1]
            # print("url:", response.url)
            # print("carModelCheck:", carModelCheck)
            # input("stop")
        else:
            carModelCheck1 = carModelCheck
            # print("carModelCheck:", carModelCheck)
            # input("stop1")

        carModel = self.getText(response, '//div[@class="bannerContent"]//p[contains(text(), "'+carModelCheck1+'")]//text()')
        if not carModel:
            carModel = self.getText(response, '//div[@class="bannerContent"]//p[contains(text(), "'+carModelCheck2+'")]//text()')
        if not carModel:
            carModel = self.getText(response, '//div[@class="bannerContent"]//p/span[contains(text(), "'+carModelCheck1+'")]/text()')

        MonthlyPayment = self.remove_gbp(self.getText(response, '//p[@class="price"]/span/text()'))
        CarimageURL = self.getText(response, '//div/@data-original')

        dataText = self.getTextAll(response, '//p//strong[contains(text(), "Free2Move Lease")]//text()')
        years = dataText.split("per month for")[1].split("years")[0]
        duration  = self.reText(years, r'([\d\.\,]+)')
        if "2" in duration:
            DurationofAgreement = '24'
        elif "3" in duration:
            DurationofAgreement = '36'
        elif "4" in duration:
            DurationofAgreement = '48'
        elif "5" in duration:
            DurationofAgreement = '60'
        else:
            DurationofAgreement = str()

        AverageMilesPerYear = dataText.split("initial payment, ")[1].split("miles per")[0]

        # print("url: ", response.url)
        # print("carModel: ", carModel)
        # print("AverageMilesPerYear: ", AverageMilesPerYear)
        # print("duration: ", DurationofAgreement)
        # print("dataText: ", dataText)
        # input("stop")

        TypeofFinance = 'Business Contract Hire'
        item = CarItem()
        item['CarMake'] = 'Citroen'
        item['CarModel'] = self.remove_special_char_on_excel(carModel)
        item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        match = re.search(r'([\D]+)([\d,]+)',MonthlyPayment)
        MonthlyPayment=int(match.group(2).replace(',',''))
        item['MonthlyPayment'] = MonthlyPayment
        item['CustomerDeposit'] = ''
        item['RetailerDepositContribution'] = ''
        item['OnTheRoadPrice'] = ''
        item['OptionalPurchase_FinalPayment'] =  ''
        item['AmountofCredit'] =  ''
        item['DurationofAgreement'] = DurationofAgreement
        item['TotalAmountPayable'] = ''
        item['OptionToPurchase_PurchaseActivationFee'] = ''
        item['RepresentativeAPR'] = ''
        item['FixedInterestRate_RateofinterestPA'] = ''
        item['ExcessMilageCharge'] = ''
        item['AverageMilesPerYear'] = AverageMilesPerYear
        # item['OfferExpiryDate'] = OfferExpiryDate
        item['RetailCashPrice'] =  ''
        item['CarimageURL'] = CarimageURL
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        termsUrl = 'https://www.citroen.co.uk/terms-and-conditions'
        yield Request(termsUrl, callback=self.parse_for_expirydate_bch, headers=self.headers, dont_filter=True, meta={"item":item})
        # yield item

    def parse_for_expirydate_bch(self, response):
        """Offer expiry date
        """
        item = response.meta['item']
        termsData = self.getTextAll(response, '//div[@class="zonetexte"]/p//text()')
        OfferExpiryDate = termsData.split("ordered and delivered between")[1].split("and")[0].split("-")[1].strip()
        # print("Engine_price", termsData)
        # input("stop")
        item['OfferExpiryDate'] = OfferExpiryDate.replace("/21", "/2021")
        yield item

    def parse_model(self, response):

        pcp_url = response.url+"personal-contract-purchase"
        hp_url = response.url+"hire-purchase"
        url_type = [pcp_url,hp_url]
        for url in url_type:
            yield Request(url, callback=self.parse_trim, headers=self.headers)

    def parse_trim(self, response):

        # offer_data = self.getText(response, '//p[@class="small"]/span/text()')
        # if not offer_data:
        #     offer_data = self.getText(response, '//p[contains(text(), "2019")]/text()')
        # if not offer_data:
        #     offer_data = self.getText(response, '//p/span[contains(text(), "2019")]/text()')
        #
        # OfferExpiryDate = offer_data.split("models until")[1].split(".")[0]


        imageUrl = self.getText(response, '//div[@class="offer-header__slider"]/ul/li/img/@src')
        carImageURL = 'https://info.citroen.co.uk' + imageUrl
        WebpageURL = response.url

        dataQuotePcp = self.getText(response, '//div[@id="finance-quote-pcp"]/@data-quote-reference')
        dataQuoteHp = self.getText(response, '//div[@id="finance-quote-hp"]/@data-quote-reference')
        json_linkPcp = 'https://services.codeweavers.net/public/v3/JsonFinance/RetrieveQuote?ApiKey=Y8K6DIv6VE17Bn4GP6&QuoteReference='+dataQuotePcp+'&Referrer=https:%2F%2Finfo.citroen.co.uk%2Fnew-cars%2Fcar-range%2Fcitroen-c3%2Foffers%2Fpersonal-contract-purchase&SystemKey=Citroen'
        json_linkHp = 'https://services.codeweavers.net/public/v3/JsonFinance/RetrieveQuote?ApiKey=Y8K6DIv6VE17Bn4GP6&QuoteReference='+dataQuoteHp+'&Referrer=https:%2F%2Finfo.citroen.co.uk%2Fnew-cars%2Fcar-range%2Fcitroen-c3%2Foffers%2Fpersonal-contract-purchase&SystemKey=Citroen'
        car_type = [json_linkPcp,json_linkHp]
        for json_link in car_type:
            yield Request(json_link, callback=self.parse_items,  meta={"WebpageURL":WebpageURL, "carImageURL":carImageURL})

    def parse_items(self, response):
        CarModel = str()
        OnTheRoadPrice = str()
        MonthlyPayment = str()
        CustomerDeposit = str()
        DurationofAgreement = str()
        AmountofCredit = str()
        TotalAmountPayable = str()
        OptionalPurchase_FinalPayment = str()
        ExcessMileageRate = str()
        FixedInterestRate_RateofinterestPA = str()
        RepresentativeAPR = str()
        AnnualMileage = str()
        totalDepositContribution = str()
        offerExpiredDate = str()

        # FinalPayment = str()

        carImageURL = response.meta.get('carImageURL')
        # OfferExpiryDate = response.meta.get('OfferExpiryDate')
        data_json = json.loads(response.body)
        # print("url:", response.url)
        # print("data_json:", data_json)
        # input("stop")
        if data_json['HasError'] == True:
            return
        else:
            WebpageLink = response.meta.get('WebpageURL')
            TypeofFinance = data_json.get('Key') # HIRE PURCHASE # PERSONAL CONTRACT PURCHASE

            if "PERSONAL CONTRACT PURCHASE" in TypeofFinance:
                if "personal-lease" in WebpageLink:
                    WebpageURL = WebpageLink.replace("personal-leasehire-purchase", "personal-contract-purchase")
                else:
                    WebpageURL = WebpageLink.replace("hire-purchase", "personal-contract-purchase")
            elif "personal-leasehire-purchase" in WebpageLink:
                WebpageURL = WebpageLink.replace("personal-leasehire-purchase", "hire-purchase")
            else:
                WebpageURL = WebpageLink

            if "Vehicle" in data_json:
                CarModel = data_json['Vehicle']['Model']
            if "Quote" in data_json:
                OnTheRoadPrice = data_json['Quote']['CashPrice']
                # print("url:", response.url)
                # print("CarModel:", CarModel)
                # print("OnTheRoadPrice:", OnTheRoadPrice)
                # input("stop")
                MonthlyPayment = data_json['Quote']['AllInclusiveRegularPayment']
                CustomerDeposit = data_json['Quote']['CashDeposit'] ### old Deposit
                DurationofAgreement = data_json['Quote']['Term']
                AmountofCredit = data_json['Quote']['Balance']
                TotalAmountPayable = data_json['Quote']['TotalAmountPayable']
                OptionalPurchase_FinalPayment = data_json['Quote']['Residual']
                ExcessMileageRate = data_json['Quote']['ExcessMileageRate']
                FixedInterestRate_RateofinterestPA = data_json['Quote']['RateOfInterest']
                RepresentativeAPR = data_json['Quote']['Apr']
                AnnualMileage = data_json['Quote']['AnnualMileage']
                totalDepositContribution = data_json['Quote']['DepositContribution']
                ### ITS fINE (Different on web and Json)###
                # offerExpiredDate = data_json['Vehicle']['RegistrationDate']
                ### ITS fINE ###

                # FinalPayment = data_json['Quote']['CostBreakdown']['OtrPrice']
                ### PCP ###
                item = CarItem()
                item['CarMake'] = 'Citroen'
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
                item['MonthlyPayment'] = float(MonthlyPayment)
                item['CustomerDeposit'] = float(CustomerDeposit)
                item['RetailerDepositContribution'] = float(totalDepositContribution)
                item['OnTheRoadPrice'] = float(OnTheRoadPrice)
                # item['FinalPayment'] = FinalPayment
                item['OptionalPurchase_FinalPayment'] =  OptionalPurchase_FinalPayment
                item['AmountofCredit'] =  AmountofCredit
                item['DurationofAgreement'] = DurationofAgreement
                item['TotalAmountPayable'] = TotalAmountPayable
                item['OptionToPurchase_PurchaseActivationFee'] = ''
                item['RepresentativeAPR'] = RepresentativeAPR
                item['FixedInterestRate_RateofinterestPA'] = FixedInterestRate_RateofinterestPA
                item['ExcessMilageCharge'] = ExcessMileageRate
                item['AverageMilesPerYear'] = AnnualMileage
                # item['OfferExpiryDate'] = offerExpiredDate.split('T')[0]
                item['OfferExpiryDate'] = '30/06/2022'
                item['RetailCashPrice'] =  OnTheRoadPrice
                item['CarimageURL'] = carImageURL
                item['WebpageURL'] = WebpageURL
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                if "PCP" not in item['TypeofFinance']:
                    yield item

            #### Citroen VANS START HERE ###

    def parse_vans(self, response):

        link = response.xpath('//div[@id="offers-results"]//div[@class="vehicles"]//a')
        for a in link:
            href = response.urljoin(self.getText(a, './@href'))
            if "car-range" not in href:
                # url = str()
                # print("url: ", response.url)
                # print("href: ", href)
                # input("stop")
                yield Request(href, callback=self.parse_van_items, headers=self.headers)

    def parse_van_items(self, response):

        carModelChecks = self.getText(response, '//h1[@class="header q-headline q-rte-container"]//text()')
        carModel = carModelChecks.split("LATEST")[0]
        # carModelCheck = carModelChecks.split(" ")[0]
        # carModel = self.getText(response, '//div[@class="bannerContent"]//p[contains(text(), "'+carModelCheck+'")]/text()')
        # if not carModel:
        #     carModel = carModelChecks
        # print("url: ", response.url)
        # print("carModel: ", carModelChecks)
        # # print("carModel: ", carModel)
        # input("stop")

        MonthlyPayment = self.remove_gbp(self.getText(response, '//h3[@class="q-subheadline q-rte-container"]//span/b/text()'))
        if not MonthlyPayment:
            MonthlyPayment = self.remove_gbp(self.getText(response, '//h3[@class="q-subheadline q-rte-container"]//span/span/text()'))
            # regex = r"[\$|€|£\20AC\00A3]{1}\d+\.?\d{0,2}"
            # MonthlyPayment = re.search(regex, MonthlyPayment).group()
        CarimageURL = self.getText(response, '//picture/source/@srcset')

        typeOfFinance = 'Commercial Contract Hire'

        # print("vCarimageURL: ", CarimageURL)
        # print("MonthlyPayment: ", MonthlyPayment)
        # input("stop")

        # all_paragraph = self.getTextAll(response, '//div[@class="q-offer-content"]//p[contains(text(), "per month") or contains(text(), "Free2Move") or contains(text(), "miles per year")]//text()')
        all_paragraph = response.xpath('//div[@class="q-offer-content"]/p//text()').extract()
        if all_paragraph:
            all_paragraph = all_paragraph[2]
            # print("all_paragraph: ", all_paragraph)
            # # print("DurationofAgreement: ", DurationofAgreement)
            # input("stop")


            if "2 years" in all_paragraph:
                DurationofAgreement = '24'
            elif "3 years" in all_paragraph:
                DurationofAgreement = '36'
            elif "4 years" in all_paragraph:
                DurationofAgreement = '48'
            elif "5 years" in all_paragraph:
                DurationofAgreement = '60'
            else:
                DurationofAgreement = str()

            # offerExp = all_paragraph
            # offerExp = offerExp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
            # offerExpiredDate = self.dateMatcher(offerExp)[0]

        # print("all_paragraph: ", all_paragraph)
        # print("offerExpiredDate: ", offerExpiredDate)
        # print("DurationofAgreement: ", DurationofAgreement)
        # input("stop")

        # if "finance-lease" in response.url:
        #     all_paragraph = self.getText(response, '//div[@class="tabs__content__tab__inner"]//p[contains(text(), "per month")]/text()')
        #     if all_paragraph:
        #         regex = r"[\$|€|£\20AC\00A3]{1}\d+(?:,\d+){0,2}"
        #         MonthlyPayment = self.remove_gbp(re.search(regex, all_paragraph).group())
        #         if "initial payment of" in all_paragraph:
        #             deposit = all_paragraph.split("initial payment of")[1]
        #             CustomerDeposit = self.remove_gbp(deposit.split("and a balloon payment")[0])

            # ### CH,  ###
            item = CarItem()
            item['CarMake'] = 'Citroen'
            item['CarModel'] = self.remove_special_char_on_excel(carModel)
            item['TypeofFinance'] = typeOfFinance
            if MonthlyPayment:
                item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
            else:
                item['MonthlyPayment'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['DurationofAgreement'] = DurationofAgreement
            item['CustomerDeposit'] = 'N/A'
            item['AmountofCredit'] =  'N/A'
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = ''
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['OfferExpiryDate'] = '31/03/2022'
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['RetailerDepositContribution'] = 'N/A'
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = '10000'
            item['RetailCashPrice'] =  'N/A'
            item['CarimageURL'] = CarimageURL
            item['DebugMode'] = self.Debug_Mode
            item['WebpageURL'] = response.url
            try:
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            except:
                item['FinalPaymentPercent'] = float()
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            yield item
