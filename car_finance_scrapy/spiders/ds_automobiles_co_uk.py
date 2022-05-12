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

### PCP Cars
### CONTRACT HIRE Cars
### VANS All
#personal-lease
#hire-purchase
#personal-contract-purchase
 # 'https://info.driveds.co.uk/finance-calculator/',
class DsAutomobilesSpider(BaseSpider):
    name = "dsautomobiles.co.uk"

    allowed_domains = ['dsautomobiles.co.uk', 'info.driveds.co.uk']
    base_url  = 'https://www.dsautomobiles.co.uk'
    start_url = ['https://www.dsautomobiles.co.uk/ds-offers', 'https://www.dsautomobiles.co.uk/ds-offers/ds-business-offers', 'https://store.dsautomobiles.co.uk/configurable/finance/','https://store.dsautomobiles.co.uk/trim/configurable/finance/ds-7-crossback-suv?_ga=2.100113629.2112852411.1617886590-647324177.1617785803', 'https://store.dsautomobiles.co.uk/trim/configurable/finance/ds-3-crossback-suv?_ga=2.100113629.2112852411.1617886590-647324177.1617785803', 'https://store.dsautomobiles.co.uk/trim/configurable/finance/ds-9-saloon?_ga=2.100113629.2112852411.1617886590-647324177.1617785803']
    api_url = 'https://api.groupe-psa.com/applications/onlinefinance-simulation-offer/v1/financialsimulation/offer/servicelevels/criteriacompatibility'
    ### Car both PCP and BCH

    headers_ds = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Host': 'api.groupe-psa.com',
        'Origin': 'https://store.dsautomobiles.co.uk/',
        'Referer': 'https://store.dsautomobiles.co.uk/',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
        'x-ibm-client-id': '4b1a1cd8-776f-4309-868d-e74ad4c39d83'
    }

    def __init__(self):
        super(DsAutomobilesSpider, self).__init__()

    def start_requests(self):
        for url in self.start_url:
            if "business-offers" in url:
                yield Request(url, callback=self.parse_business_cars, headers=self.headers)
            # elif "/finance-calculator/" in url:
            #     yield Request(url, callback=self.parse_pcp_calculator, headers=self.headers)
            elif "/trim/configurable/finance" in url:### configurable Calculator Own Value put
                # print("url",url)
                # input("stop")
                yield Request(url, callback=self.parse_pcp_config_calculator, headers=self.headers, dont_filter=True)
            elif "configurable/finance" in url:
                yield Request(url, callback=self.parse_pcp_offers, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_car, headers=self.headers)

    def parse_car(self, response):
        link = response.xpath('//div[@id="section-cars"]//article[@class="car main-car  offer-hire-purchase  offer-personal-lease  offer-personal-contract-purchase  offer-simplydrive  offer-motability  offer-business  btn-sm-visible noselect"]//a')
        for a in link:
            href = self.getText(a, "./@href")
            url = response.urljoin(href)
            # if "offers/" in url:
                # print("url", url)
                # print("url",response.url)
                # input("stop")
            yield Request(url, callback=self.parse_model, headers=self.headers)

    def parse_pcp_offers(self, response):
        """PCP CONFG OFFERS- Representative OFFER
        """
        link = response.xpath('//div[contains(@class, "OfferGridStyled")]//div[@class="carTitleWrap"]')
        for a in link:
            href = self.getText(a, "./a/@href")
            url = response.urljoin(href)
            # print("url: ", url)
            # input("stop")
            yield Request(url, callback=self.parse_pcp_offers_data_url, headers=self.headers)

    def parse_pcp_config_calculator(self, response):
        json_string = self.getText(response, '//script[@id="__NEXT_DATA__"]/text()')
        JO = json.loads(json_string)
        trims = JO['props']['initialState']['TrimSelector']['configurable']['trims']
        # print("url", response.url)
        # print("trims", trims)
        # input("stop")
        for trim in trims:
            id = trim['_id']
            lcdv16Code = id.split("+")[0]
            options_code_2 = id.split("+")[1]
            options_code_1 = id.split("+")[2]
            prices_object = trim['_properties']['object']['prices']
            Model_name = trim['_properties']['object']['nameplate']['description']
            Model_name_varient = trim['_properties']['object']['specPack']['title']
            Model_name_id = trim['_properties']['object']['nameplate']['id']
            required_prices = [(i) for i in prices_object if i['type']=="Employee"]
            basicPriceInclTax = required_prices[0]['inputPriceInclTax']
            complete_model_name = Model_name +" "+ Model_name_varient
            engine_specification_object = trim['_properties']['object']['engine']['specs']
            fiscalProperties_co2Emissions_object = [(i) for i in engine_specification_object if i['label']=="CO2 combined (g/km)"][0]
            fiscalProperties_co2Emissions_value = fiscalProperties_co2Emissions_object['value']
            extraFields_object = trim['_properties']['object']['extraFields']['pricesV2'][1]
            registrationFee = extraFields_object['breakdown']['registrationFee']
            delivery = extraFields_object['breakdown']['deliveryInclTax']
            roadFundLicence = extraFields_object['breakdown']['vehicleExciseDuty']
            # productKey =  trim['_properties']['object']['financeProducts'][0]['key']
            productKey = 'SOL_PCP_B2C'

            # print("url", response.url)
            # print("prices_object", prices_object)
            # print("Model_name", Model_name)
            # print("Model_name_id", Model_name_id)
            # print("required_prices", required_prices)
            # print("basicPriceInclTax", basicPriceInclTax)
            # print("complete_model_name", complete_model_name)
            # print("productKey", productKey)
            # print("registrationFe", registrationFee)
            # print("options_code_2", options_code_2)
            # print("options_code_1", options_code_1)
            # print("lcdv16Code", lcdv16Code)
            #
            # input("stop")


            duration_limit = [37,42,48]
            for duration in duration_limit:
                deposit = 2000
                annualMileage = 10000

                payload = '''{
                	"context": {
                		"siteCode": "SME",
                		"journeyType": "ACVNR",
                		"distributionBrand": "DS",
                		"countryCode": "GB",
                		"languageCode": "en",
                		"customer": {
                			"clientType": "P"
                		},
                		"componentCode": "WID"
                	},
                	"vehicle": {
                		"pricing": {
                			"basicPriceInclTax": '''+str(basicPriceInclTax)+''',
                			"netPriceInclTax": '''+str(basicPriceInclTax)+'''
                		},
                		"fiscalProperties": {
                			"co2Emissions": '''+str(fiscalProperties_co2Emissions_value)+''',
                			"registrationFees": '''+str(registrationFee)+''',
                			"roadFundLicence": '''+str(roadFundLicence)+'''
                		},
                		"lcdv16Code": "'''+str(lcdv16Code)+'''",
                		"otrCosts": {
                			"delivery": {
                				"amountInclTax": '''+str(delivery)+'''
                			}
                		},
                		"options": [{
                			"code": "'''+str(options_code_1)+'''",
                			"pricing": {
                				"basicPriceInclTax": 0,
                				"netPriceInclTax": 0
                			}
                		}, {
                			"code": "'''+str(options_code_2)+'''",
                			"pricing": {
                				"basicPriceInclTax": 0,
                				"netPriceInclTax": 0
                			}
                		}]
                	},
                	"parameters": {
                		"duration": '''+str(duration)+''',
                		"deposit": '''+str(deposit)+''',
                		"depositAmountKind": "MT",
                		"depositAmountNature": "TC",
                		"annualMileage": '''+str(annualMileage)+''',
                		"productKey": "'''+str(productKey)+'''",
                		"services": []
                	}
                }'''

                yield Request(self.api_url, callback=self.parse_condig_calculator_data, method="POST", body=payload, headers=self.headers_ds, meta={"car_model_name":complete_model_name}, dont_filter=True)


    def parse_condig_calculator_data(self, response):
        JO = json.loads(response.body)
        # print("url", response.url)
        # print("JO", JO)
        # input("stop")
        carModel = response.meta['car_model_name']
        packageSelectionObject = JO['packageSelection'][0]
        # print("packageSelectionObject", packageSelectionObject)
        # input("stop")
        financingDetailsObject = packageSelectionObject['financingDetails'][0]
        MonthlyPayments = packageSelectionObject['price']
        displayLinesObject = financingDetailsObject['displayLines']

        DurationofAgreement = [(i) for i in displayLinesObject if "Term of Agreement" in i['label']][0]
        CustomerDeposit = [(i) for i in displayLinesObject if "Customer Deposit" in i['label']][0]
        OnTheRoadPrice = [(i) for i in displayLinesObject if "DS Online Price/Cash Price" in i['label']][0]
        OptionalPurchase_FinalPayment = [(i) for i in displayLinesObject if "Optional Final Payment" in i['label']][0]
        AmountofCredit = [(i) for i in displayLinesObject if "Total Amount of Credit" in i['label']][0]
        TotalAmountPayable = [(i) for i in displayLinesObject if "Total Amount Payable" in i['label']][0]
        RepresentativeAPR = [(i) for i in displayLinesObject if "APR" in i['label']][0]
        FixedInterestRate_RateofinterestPA = [(i) for i in displayLinesObject if "Fixed Rate of Interest per Year" in i['label']][0]
        ExcessMilageCharge = [(i) for i in displayLinesObject if "Excess Mileage Charge" in i['label']][0]
        AnnualMileage = [(i) for i in displayLinesObject if "Annual Mileage" in i['label']][0]

        import datetime
        expiry_date = datetime.date.today() + timedelta(days=14)
        formated_date_expiry = expiry_date.strftime('%d/%m/%Y')


        item = CarItem()
        item['CarMake'] = 'DS Automobiles'
        item['CarModel'] = self.remove_special_char_on_excel(carModel)
        item['TypeofFinance'] = self.get_type_of_finance("PCP")
        item['MonthlyPayment'] = MonthlyPayments
        item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit['value'])
        item['RetailerDepositContribution'] = "N/A"
        item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice['value'])
        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment['value'])
        item['AmountofCredit'] = self.remove_gbp(AmountofCredit['value'])
        item['DurationofAgreement'] = DurationofAgreement['value']
        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable['value'])
        item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
        item['RepresentativeAPR'] = RepresentativeAPR['value']
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA['value'])
        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge['value'])
        item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage['value'])
        item['OfferExpiryDate'] = formated_date_expiry
        item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice['value'])
        item['CarimageURL'] = ''
        item['WebpageURL'] = 'https://store.dsautomobiles.co.uk/configurable/finance/'
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        yield item


    def parse_pcp_offers_data_url(self, response):
        """DATA PCP OFFERS
        """
        # print("resp: ", response.url)
        # input("sto")
        dataJson = self.getText(response, '//script[contains(text(), "TrimSelector")]/text()')
        dataJson = json.loads(dataJson)

        initialState = dataJson['props']['initialState']
        Content = initialState['Content']
        # offerExp = Content.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        # OfferExpiryDate = self.dateMatcher(offerExp)[1]

        # print("resp: ", response.url)
        # print("dataJson: ", dataJson)
        # print("Content: ", Content)
        # input("sto")
        TrimSelector = initialState['TrimSelector']['configurable']
        trims = TrimSelector['trims']
        for trim_data in trims:
            trim_id = trim_data['_id']
            CarModel = trim_data['title']
            CarimageURL = trim_data['images'][0]['url']

            url = "https://store.dsautomobiles.co.uk/fc/api/v3/4/en/calculate-for-summary"

            payload = "{\"carConfigId\":\""+trim_id+"\"}"
            headers = {
                'content-type': "application/json",
                'cache-control': "no-cache",
                'postman-token': "438adbd2-0d5b-90ed-5d43-c542b58f8f35"
                }

            responses = requests.request("POST", url, data=payload, headers=headers)
            Offer_data = json.loads(responses.text)
            # print("Offer_data: ", Offer_data)
            # print("CarModel: ", CarModel)
            # input("sto")
            blocks = Offer_data['blocks'][0]

            displayLines = blocks['displayLines']
            data = dict()
            for carOffers in displayLines:
                label = carOffers['label']
                value = carOffers['value']
                data.update({label:value})
            OnTheRoadPrice = data['DS Online Price/Cash Price']
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
            if "APR" in data:
                RepresentativeAPR = data['APR']
            elif "Representative APR" in data:
                RepresentativeAPR = data['Representative APR']
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
            item['CarMake'] = 'DS Automobiles'
            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = 'Personal Contract Purchase'
            item['MonthlyPayment'] =  self.make_two_digit_no(MonthlyPayment)
            item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
            item['RetailerDepositContribution'] = 'N/A'
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
            # item['OfferExpiryDate'] = OfferExpiryDate ### 31 March 2021
            item['OfferExpiryDate'] = 'N/A'
            # termsUrl = 'https://www.citroen.co.uk/terms-and-conditions'
            # yield Request(termsUrl, callback=self.parse_for_expirydate_main_offer, headers=self.headers, dont_filter=True, meta={"item":item})
            yield item


    ########### CALCULATOR #######
    def parse_pcp_calculator(self, response):
        """PCP calculator DATA
        """

        url = "https://services.codeweavers.net/api/vehicleselection/datasets/PSA/options"
        headers = {
            'accept': "application/json, text/plain, */*",
            'content-type': "application/json;charset=UTF-8",
            'origin': "https://plugins.codeweavers.net",
            'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            'x-cw-apikey': "Citroen-1FEaVw7iw4lP1xe5B3",
            'x-cw-applicationname': "Plugin PSA",
            'cache-control': "no-cache",
            'postman-token': "4241eafe-8f8d-7019-402b-e8d75af01f8e"
        }

        payload = '{"PreviouslySelectedOptions":["Car","DS"],"AllowedManufacturers":[]}'

        response = requests.request("POST", url, data=payload, headers=headers)
        data = json.loads(response.text)
        Options = data['Options']
        for model in Options:
            modelName = model['Display'] ### Model NAME

            url = "https://services.codeweavers.net/api/vehicleselection/datasets/PSA/options"

            payload = '{"PreviouslySelectedOptions":["Car","DS","'+modelName+'"],"AllowedManufacturers":[]}'
            headers = {
                'accept': "application/json, text/plain, */*",
                'content-type': "application/json;charset=UTF-8",
                'origin': "https://plugins.codeweavers.net",
                'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                'x-cw-apikey': "Citroen-1FEaVw7iw4lP1xe5B3",
                'x-cw-applicationname': "Plugin PSA",
                'cache-control': "no-cache",
                'postman-token': "4241eafe-8f8d-7019-402b-e8d75af01f8e"
            }


            response = requests.request("POST", url, data=payload, headers=headers)
            Vardata = json.loads(response.text)
            # print("url", response.url)
            # print("Vardata: ", Vardata)
            # input("stop")
            VarOptions = Vardata['Options']
            for varient in VarOptions:
                var_type = varient['Display'] ### VARIETN NAME
                url = "https://services.codeweavers.net/api/vehicleselection/datasets/PSA/options"

                payload = '{"PreviouslySelectedOptions":["Car","DS","'+modelName+'","'+var_type+'"],"AllowedManufacturers":[]}'
                headers = {
                    'accept': "application/json, text/plain, */*",
                    'content-type': "application/json;charset=UTF-8",
                    'origin': "https://plugins.codeweavers.net",
                    'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
                    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                    'x-cw-apikey': "Citroen-1FEaVw7iw4lP1xe5B3",
                    'x-cw-applicationname': "Plugin PSA",
                    'cache-control': "no-cache",
                    'postman-token': "4241eafe-8f8d-7019-402b-e8d75af01f8e"
                }
                Der_response = requests.request("POST", url, data=payload, headers=headers)
                Derv_data = json.loads(Der_response.text)
                DerOptions = Derv_data['Options']

                for derivative in DerOptions:
                    der_type = derivative['Display'] ### Derivative NAME
                    der_code = derivative['Id'] ### Derivative CODE

                    url = "https://services.codeweavers.net/api/vehicleselection/datasets/PSA/options"

                    payload = '{"PreviouslySelectedOptions":["Car","DS","'+modelName+'","'+var_type+'","'+der_code+'"],"AllowedManufacturers":[]}'
                    headers = {
                        'accept': "application/json, text/plain, */*",
                        'content-type': "application/json;charset=UTF-8",
                        'origin': "https://plugins.codeweavers.net",
                        'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
                        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                        'x-cw-apikey': "Citroen-1FEaVw7iw4lP1xe5B3",
                        'x-cw-applicationname': "Plugin PSA",
                        'cache-control': "no-cache",
                        'postman-token': "4241eafe-8f8d-7019-402b-e8d75af01f8e"
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
            payload = '{"Credentials":{"ApiKey":"1FEaVw7iw4lP1xe5B3","SystemKey":"Citroen","Referrer":"https://www.dsautomobiles.co.uk/"},"VehicleRequests":[{"Id":"Finance Plugin","BuildToOrderVehicle":{"Identifier":"'+Vehicle_Identifier+'","IdentifierType":"Titre","Type":"Car","SelectedOptions":[{"Code":"'+Engine_Code+'","Price":"'+str(Engine_price)+'"}]},"Parameters":{"DepositType":"Amount","RegularPayment":200,"IsTelematics":false,"AddTelematics":false,"CalculationType":"ToRegularPayment","CashValuesAreVatExclusive":false,"CashDeposit":2000,"Term":48,"AnnualMileage":6000}}],"Customer":{}}'

            # payload = '{"Credentials":{"ApiKey":"1FEaVw7iw4lP1xe5B3","SystemKey":"DS","Referrer":"https://info.citroen.co.uk/finance/car-finance-part-exchange-calculator/"},"VehicleRequests":[{"Id":"Finance Plugin","BuildToOrderVehicle":{"Identifier":"'+Vehicle_Identifier+'","Type":"car","SelectedOptions":[{"Code":"'+Engine_Code+'","Price":"'+str(Engine_price)+'"}]},"Parameters":{"DepositType":"Amount","RegularPayment":200,"IsTelematics":false,"AddTelematics":false,"CalculationType":"ToRegularPayment","CashDeposit":2000}}],"Customer":{}}'

            headers = {
                'accept': "application/json, text/plain, */*",
                'content-type': "application/json;charset=UTF-8",
                'origin': "https://plugins.codeweavers.net",
                'referer': "https://plugins.codeweavers.net/finance-plugins/v1/psa",
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                'x-cw-apikey': "Citroen-1FEaVw7iw4lP1xe5B3",
                'x-cw-applicationname': "Plugin PSA",
                'cache-control': "no-cache",
                'postman-token': "4241eafe-8f8d-7019-402b-e8d75af01f8e"
            }

            car_Data = requests.request("POST", url, data=payload, headers=headers)
            full_data = json.loads(car_Data.text)
            # print("url", full_data)
            # print("data", response.url)
            # input("stop")

            Vehicles = full_data['Vehicles'][0]
            FinanceQuotations = Vehicles['FinanceQuotations'][0] ### FOR PCP
            # print("url", FinanceQuotations)
            # print("data", response.url)
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

                    # print("data", data)
                    # input("stop")

                    OnTheRoadPrice = data['VehiclePrice']
                    AmountofCredit = data['AmountOfCredit']

                    if "RegularPayment" in data:
                        MonthlyPayment = data['RegularPayment']
                    elif "TotalRegularPayment" in data:
                        MonthlyPayment = data['TotalRegularPayment']
                    else:
                        MonthlyPayment = 'N/A'
                    CustomerDeposit = data['CustomerCashDeposit']
                    TotalAmountPayable = data['TotalAmountPayable']
                    DurationofAgreement = data['TermOfAgreement']

                    if "Apr" in data:
                        RepresentativeAPR = data['Apr']
                    elif "Representative APR" in data:
                        RepresentativeAPR = data['Representative APR']
                    elif "APR" in data:
                        RepresentativeAPR = data['APR']    
                    else:
                        RepresentativeAPR = 'N/A'       

                    FixedInterestRate_RateofinterestPA = data['FixedRateOfInterest']

                    if 'OptionalFinalPayment' in data:
                        OptionalPurchase_FinalPayment = data['OptionalFinalPayment']
                    else:
                        OptionalPurchase_FinalPayment = 'N/A'
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

                    # print("url", carModel)
                    # print("data", data)
                    # input("stop")


                    item = CarItem()
                    item['CarMake'] = 'DS Automobiles'
                    item['CarModel'] = self.remove_special_char_on_excel(carModels)
                    item['TypeofFinance'] = self.get_type_of_finance('PCP')
                    item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                    item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                    item['RetailerDepositContribution'] = RetailerDepositContribution
                    item['OnTheRoadPrice'] = OnTheRoadPrice
                    item['OptionalPurchase_FinalPayment'] =  OptionalPurchase_FinalPayment
                    item['AmountofCredit'] =  AmountofCredit
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                    item['TotalAmountPayable'] = TotalAmountPayable
                    item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                    item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMileageRate)
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage)
                    item['OfferExpiryDate'] = 'N/A'
                    item['RetailCashPrice'] =  OnTheRoadPrice
                    item['CarimageURL'] = ''
                    item['WebpageURL'] = 'https://info.driveds.co.uk/finance-calculator/'
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    try:
                        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    except:
                        item['DepositPercent'] = float()
                    yield item

    def parse_model(self, response):
        #########################
        ### PCP CARS ###
        #########################
        financeType = self.getTexts(response, '//div[@id="section-tabs"]//div[@class="tabs__header__content__inner"]/ul/li/text()')
        for types in financeType:
            if "PCP" in types:
                pcpLoop = response.xpath('//div[@class="model-tables hidden-lg"]/div[@class="model-col"]')
                for data in pcpLoop:
                    modelPrefix = self.getTextAll(data, './/p[@class="mTitle"]/text()')
                    # modelPostfix = self.getTextAll(data, './/p[@class="mSubTitle"]/text()')
                    carModel = modelPrefix
                    carimage = self.getText(data, './div[@class="model-thumb"]/img/@src')
                    MonthlyPayment = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "monthly payments of")]/following-sibling::td/text()')
                    CustomerDeposit = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Customer deposit")]/following-sibling::td/text()')
                    DepositContribution = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "deposit contribution")]/following-sibling::td/text()')
                    DurationofAgreement = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Duration of Agreement")]/following-sibling::td/text()')
                    OptionalPurchase_FinalPayment = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Optional final payment")]/following-sibling::td/text()')
                    OnTheRoadPrice = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "OTR Price")]/following-sibling::td/text()')
                    AmountOfCredit = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/text()')
                    TotalAmountPayable = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/text()')
                    FixedInterestRate_RateofinterestPA = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Interest rate")]/following-sibling::td/text()')
                    RepresentativeAPR = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Representative APR") or contains(text(), "APR")]/following-sibling::td/text()')
                    OptionToPurchase_PurchaseActivationFee = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Credit Facility Fee")]/following-sibling::td/text()')
                    AnnualMileage = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Annual Mileage")]/following-sibling::td/text()')
                    ExcessMilageCharge = self.getText(data, './/div[@class="model-pricing-table"]/table/tr/td[contains(text(), "Excess Mileage Charge")]/following-sibling::td/text()')



                    item = CarItem()
                    item['CarMake'] = 'DS Automobiles'
                    item['CarModel'] = self.remove_special_char_on_excel(carModel)
                    item['TypeofFinance'] = self.get_type_of_finance('PCP')
                    item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                    item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                    item['RetailerDepositContribution'] = self.remove_gbp(DepositContribution)
                    item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
                    item['OptionalPurchase_FinalPayment'] =  self.remove_gbp(OptionalPurchase_FinalPayment)
                    item['AmountofCredit'] =  self.remove_gbp(AmountOfCredit)
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                    item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
                    item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(OptionToPurchase_PurchaseActivationFee)
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                    item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage)
                    item['OfferExpiryDate'] = 'N/A'
                    item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice)
                    item['CarimageURL'] = carimage
                    item['WebpageURL'] = response.url
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    yield item

            elif "Lease" in types:
                #########################
                ### FINANCE LEASE CARS ###
                #########################

                TypeofFinance = types
                leaseLoop = response.xpath('//div[@class="model-tables without-table"]/div[@class="model-col"]')
                for data in leaseLoop:
                    modelPrefix = self.getText(data, './/p[@class="mTitle"]/text()')
                    modelPostfix = self.getTextAll(data, './/p[@class="mSubTitle"]/text()')
                    carModel = modelPrefix +''+ modelPostfix
                    carimage = self.getText(data, './div[@class="model-thumb"]/img/@src')
                    MonthlyPayment = self.getText(data, './/p[@class="mSubTitle bg-white"]/strong/text()')
                    CustomerDeposit = self.getText(data, './/p[@class="mSubTitle bg-white"]//strong[2]/text()')

                    item = CarItem()
                    item['CarMake'] = 'DS Automobiles'
                    item['CarModel'] = self.remove_special_char_on_excel(carModel)
                    item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
                    item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                    item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                    item['RetailerDepositContribution'] = 'N/A'
                    item['OnTheRoadPrice'] = 'N/A'
                    item['OptionalPurchase_FinalPayment'] =  'N/A'
                    item['AmountofCredit'] =  'N/A'
                    item['DurationofAgreement'] = 'N/A'
                    item['TotalAmountPayable'] = 'N/A'
                    item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                    item['RepresentativeAPR'] = ''
                    item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                    item['ExcessMilageCharge'] = 'N/A'
                    item['AverageMilesPerYear'] = '10000'
                    item['OfferExpiryDate'] = 'N/A'
                    item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice)
                    item['CarimageURL'] = carimage
                    item['WebpageURL'] = response.url
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    yield item

            elif "Hire Purchase" in types:
                imageUrl = self.getText(response, '//div[@class="offer-header__slider"]/ul/li/img/@src')
                dataQuotehp= self.getText(response, '//div[@id="finance-quote-hp"]/@data-quote-reference')
                json_linkHp = 'https://services.codeweavers.net/public/v3/JsonFinance/RetrieveQuote?ApiKey=1FEaVw7iw4lP1xe5B3&QuoteReference='+dataQuotehp+'&Referrer=https:%2F%2Finfo.driveds.co.uk%2Foffers%2Fds-7-crossback-offers%2F&SystemKey=Citroen'
                weburl = response.url

                yield Request(json_linkHp, callback=self.parse_car_item, headers=self.headers, dont_filter=True, meta={"imageUrl":imageUrl, "weburl":weburl})

    def parse_car_item(self, response):
        ########################
        ### HIRE PURCHASE CARS ###
        ########################
        carImageURL = response.meta.get('carImageURL')
        weburl = response.meta.get('weburl')
        WebpageLink = weburl+"#hire-purchase"
        data_json = json.loads(response.body)

        # print("url:", response.url)
        # print("data_json:", data_json)
        # input("stop")
        if data_json['HasError'] == True:
            return
        else:
            TypeofFinance = data_json.get('Key') # HIRE PURCHASE # PERSONAL CONTRACT PURCHASE

            if "Vehicle" in data_json:
                CarModel = data_json['Vehicle']['Model']
            if "Quote" in data_json:
                OnTheRoadPrice = data_json['Quote']['CashPrice']

                MonthlyPayment = data_json['Quote']['AllInclusiveRegularPayment']
                CustomerDeposit = data_json['Quote']['CashDeposit'] ### old Deposit
                DurationofAgreement = data_json['Quote']['Term']
                AmountofCredit = data_json['Quote']['AmountOfCredit']
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
            item['CarMake'] = 'DS Automobiles'
            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = float(MonthlyPayment)
            item['CustomerDeposit'] = float(CustomerDeposit)
            item['RetailerDepositContribution'] = float(totalDepositContribution)
            item['OnTheRoadPrice'] = float(OnTheRoadPrice)
            item['OptionalPurchase_FinalPayment'] =  OptionalPurchase_FinalPayment
            item['AmountofCredit'] =  AmountofCredit
            item['DurationofAgreement'] = DurationofAgreement
            item['TotalAmountPayable'] = TotalAmountPayable
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
            item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
            item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMileageRate)
            item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage)
            item['OfferExpiryDate'] = 'N/A'
            item['RetailCashPrice'] =  OnTheRoadPrice
            item['CarimageURL'] = carImageURL
            item['WebpageURL'] = WebpageLink
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            yield item

            ########################
            ### CONTRACT HIRE CARS ###
            ########################
    def parse_business_cars(self, response):
        """Business Contract Hire Cars
        """
        link = self.getTexts(response, '//div[@id="sections-container"]//div[@class="span_5 col"]/a/@href')
        for a in link:
            url = response.urljoin(a)
            # print("url:", response.url)
            # print("link:", url)
            # input("stop")
            yield Request(url, callback=self.parse_business_model, headers=self.headers)

    def parse_business_model(self, response):
        """BUSINESS Cars
        """
        data_loop = response.xpath('//section[contains(@class, "multicolonnes ")]//div[@class="span_3 col"]')
        for data in data_loop:
            carModel = self.getTextAll(data, './/h3[@class="multicolonnestitle h3"]//text()')
            MonthlyPayment = self.getText(data, './p/strong/text()')
            CustomerDeposit = self.getTextAll(data, './/p//span[contains(text(), "initial rental")]/text()')
            if not CustomerDeposit:
                CustomerDeposit = self.getTextAll(data, './/p[contains(text(), "initial rental")]/text()')

            if CustomerDeposit:
                regex = r"[\$|€|£\20AC\00A3]{1}\d+(?:,\d+){0,2}"
                CustomerDeposit = re.search(regex, CustomerDeposit).group()

            Carimage = self.getText(response, '//div[@class="contentImage "]/picture//img/@src')


            TypeofFinance = 'Business Contract Hire'
            DurationofAgreement = '36'

            # print("url:", response.url)
            # print("carModel:", carModel)
            # print("MonthlyPayment:", MonthlyPayment)
            # print("CustomerDeposit:", CustomerDeposit)
            # input("stop")

            item = CarItem()
            item['CarMake'] = 'DS Automobiles'
            item['CarModel'] = self.remove_special_char_on_excel(carModel)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            if MonthlyPayment:
                item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
            else:
                item['MonthlyPayment'] = ''
            if CustomerDeposit:
                item['CustomerDeposit'] = self.make_two_digit_no(str(CustomerDeposit))
            else:
                item['CustomerDeposit'] = 'N/A'
            item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['OptionalPurchase_FinalPayment'] =  'N/A'
            item['AmountofCredit'] =  'N/A'
            item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = '10000'
            item['OfferExpiryDate'] = 'N/A'
            item['RetailCashPrice'] =  'N/A'
            item['CarimageURL'] = Carimage
            item['WebpageURL'] = response.url
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            # print("item", item)
            # input("stop")
            if item['MonthlyPayment'] != '':
                yield item
