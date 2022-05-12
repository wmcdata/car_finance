# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
import urllib
from datetime import datetime, timedelta
import re
import json
import time
import requests
from urllib.parse import urljoin
from html.parser import HTMLParser
from requests import Session
# 'https://finance.skoda-auto.com/210/en-gb/api/modeldata?selectedFamilyCode=NJ'
# https://finance.skoda-auto.com/210/en-gb/api/modeldata?selectedFamilyCode=NWScala
# https://finance.skoda-auto.com/210/en-gb/api/fcapi/getfcproducts ### this will give you Product id
# 'https://finance.skoda-auto.com/210/en-gb/' ### calculator

class SkodaSpider(BaseSpider):
    name = "skoda.co.uk"

    allowed_domains = ['tools.skoda.co.uk', 'www.skoda.co.uk']
    start_url = ['https://finance.skoda-auto.com/210/en-gb/api/modeldata', 'https://www.skoda.co.uk/car-finance/new-car-offers']
    def __init__(self):
        super(SkodaSpider, self).__init__()

    def start_requests(self):
        for url in self.start_url:
            if "n-gb/api/modeldata" in url:
                yield Request(url, callback=self.parse_model_url, headers=self.headers)
            # else:
            #     yield Request(url, callback=self.parse_promotional_url, headers=self.headers)


    def parse_model_url(self, response):
        """PARSE MODELS AND DATA FROM calculator
        """

        model_json = json.loads(response.body)
        for ind , model in enumerate(model_json):
            if ind > 0:
                Code = model['Code']
                ModelNamePre = model['Title'] ### Fabia

                url = 'https://finance.skoda-auto.com/210/en-gb/api/modeldata?selectedFamilyCode='+Code

                # print("url", url)
                # input("stop")
                yield Request(url, callback=self.parse_model_code, headers=self.headers, dont_filter=True, meta={"ModelNamePre":ModelNamePre})

    def parse_model_code(self, response):
        """Calculator
        """
        ModelNamePre = response.meta['ModelNamePre']
        model_json = json.loads(response.body)
        for findModelderivative in model_json:
            ModelDataDerivatives = findModelderivative['ModelDataDerivatives']
            if ModelDataDerivatives != []:
                for DataTrims in ModelDataDerivatives:
                    ModelYear = DataTrims['ModelYear']
                    ModelDataTrimlines = DataTrims['ModelDataTrimlines']
                    for DataFuels in ModelDataTrimlines:
                        ModelDerivateTitle = DataFuels['Title'] ### SE
                        ModelDataFuels = DataFuels['ModelDataFuels']
                        for DataEngines in ModelDataFuels:
                            ModelFuelTitle = DataEngines['Title'] ### Petrol
                            ModelDataEngines = DataEngines['ModelDataEngines']
                            for ModelDetails in ModelDataEngines:
                                EngineCode = ModelDetails['Code']
                                priceModel = ModelDetails['Price']
                                ActionCode = ModelDetails['ActionCode']
                                # if ActionCode != None:
                                if ActionCode == None:
                                    VehicleKey = EngineCode
                                elif "/" in ActionCode:
                                    VehicleKey = EngineCode+'/'+ActionCode
                                else:
                                    VehicleKey = EngineCode +'/'+ ActionCode    
                                ModelNamePost = ModelDetails['Title'] ###2.0 TDI 116 PS 6G Man
                                
                                CarModel = ModelNamePre+' '+ModelDerivateTitle+' '+ModelFuelTitle+' '+ModelNamePost

                                    # print("url", response.url)
                                    # print("CarModel", CarModel)
                                    # print("CarModel", EngineCode)
                                    # print("CarModel", ActionCode)
                                    # print("CarModel", VehicleKey)
                                    # print("ModelYear", ModelYear)
                                    # input("stop")

                                producturl = "https://finance.skoda-auto.com/210/en-gb/api/fcapi/getfcproducts"

                                payload = '{"bid":"210","culture":"en-gb","domain":"","partRates":[],"product":null,"vehicle":{"key":"'+VehicleKey+'","priceModel":'+str(priceModel)+',"priceTotal":'+str(priceModel)+',"year":'+str(ModelYear)+'}}'

                                headers = {
                                    'Content-Type': 'application/json',
                                    'Cookie': 'ARRAffinity=d9094422ac7cec4ef844c67ccd19b2d30e7b96ee13c6b5a25952ff2f2e71fdc1; ARRAffinitySameSite=d9094422ac7cec4ef844c67ccd19b2d30e7b96ee13c6b5a25952ff2f2e71fdc1'
                                }

                                # print("PAYLOAD", payload)
                                # input()
                                yield Request(producturl, callback=self.parse_for_data, method='POST', headers=headers, body=payload, dont_filter=True, meta={"CarModel":CarModel, "priceModel":priceModel, "VehicleKey":VehicleKey})

    def parse_for_data(self, response):
        """Calculator data
        """
        CarModel = response.meta['CarModel']

        VehicleKey = response.meta['VehicleKey']
        priceModel = response.meta['priceModel']
        jsondata = json.loads(response.body)

        # print("url", response.url)
        # print("CarModel", CarModel)
        # print("priceModel", priceModel)
        # print("VehicleKey", VehicleKey)
        # print("jsondata", jsondata)
        # input("stop")

        if jsondata['Products'] != None:
            terms = ['24','30','36', '42', '48']
            for term in terms:
                Products = jsondata['Products']
                ProductsDefaultCode = Products['Default']
                url = 'https://finance.skoda-auto.com/210/en-gb/api/fcapi/getfcdefaults'

                payload = '{"bid":"210","culture":"en-gb","domain":"","partRates":[],"product":{"id":"'+ProductsDefaultCode+'","parameters":[{"id":"PER","text":"'+str(term)+'"},{"id":"ANM","text":"10"},{"id":"CalcTarget","text":"Rental"},{"id":"DownPayment","text":"3000"},{"id":"Rate","text":"0"},{"id":"hdnRate","text":"0"},{"id":"hdnDEP","text":"0"}]},"vehicle":{"key":"'+VehicleKey+'","priceModel":'+str(priceModel)+',"priceTotal":'+str(priceModel)+',"year":2021}}'
           
                #  '{"bid":"210","culture":"en-gb","domain":"","partRates":[],"product":{"id":"CRS479753","parameters":[]},"vehicle":{"key":"NJ32M4/MMFA9S3","priceModel":14880,"priceTotal":14880,"year":2021}}'


                headers = {
                  'Content-Type': 'application/json',
                  'Cookie': 'ARRAffinity=d9094422ac7cec4ef844c67ccd19b2d30e7b96ee13c6b5a25952ff2f2e71fdc1; ARRAffinitySameSite=d9094422ac7cec4ef844c67ccd19b2d30e7b96ee13c6b5a25952ff2f2e71fdc1'
                }

                # print("url", response.url)
                # print("CarModel", CarModel)
                # print("PAYLOAD: ", payload)
                # input("stop")
                yield Request(url, callback=self.car_result_data, method='POST', headers=headers, body=payload, dont_filter=True, meta={"CarModel":CarModel})

    def car_result_data(self, response):
        """Calculator Result
        """
        CarModel = response.meta['CarModel']
        jsondata = json.loads(response.body)

        

        if jsondata['Result'] != None:
            resultData = jsondata['Result']['Summaries'][0]
            DetailGroups = resultData['DetailGroups'][0]
            Disclaimer = DetailGroups['Disclaimer'] ### Expiry
            if Disclaimer:
                offerExp = Disclaimer.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
                OfferExpiryDate = self.dateMatcher(offerExp)[0]
            else:
                OfferExpiryDate = 'N/A' 

            Details = DetailGroups['Details']

            

            Result = dict()
            for Data in Details:
                key = Data['Label']
                value = Data['Value']
                Result.update({key:value})

            # print("url", response.url)
            # print("Details", Details)
            # print("rESULT: ", Result)
            # input("stop")    
            
            if "23 monthly payments of" in Result:
                MonthlyPayment = Result['23 monthly payments of']
            elif "29 monthly payments of" in Result:
                MonthlyPayment = Result['29 monthly payments of']
            elif "35 monthly payments of" in Result:
                MonthlyPayment = Result['35 monthly payments of']    
            elif "41 monthly payments of" in Result:
                MonthlyPayment = Result['41 monthly payments of']
            elif "47 monthly payments of" in Result:
                MonthlyPayment = Result['47 monthly payments of']


            if "Duration" in Result: ### CHECK FOR FIXING ERROR -> IN THIS CASE ONLY SHOWING MONTHLY PRICE
                DurationofAgreement = Result['Duration']
                # AnnualMileage = Result['Annual Mileage'] ### 10
                CustomerDeposit = Result['My Deposit']
                if "ŠKODA Contribution" in Result:
                    RetailerDepositContribution = Result['ŠKODA Contribution']
                else:
                    RetailerDepositContribution = 'N/A'    
                OnTheRoadPrice = Result['Retailer cash price']
                OptionalPurchase_FinalPayment = Result['Optional final payment']
                OnTheRoadPrice = Result['Retailer cash price']
                OptionToPurchase_PurchaseActivationFee = Result['Option to purchase fee**']
                TotalAmountPayable = Result['Total amount payable']
                AmountofCredit = Result['Total amount of credit']
                ExcessMilageCharge = Result['Excess mileage (per mile)***']
                RepresentativeAPR = Result['Representative APR']
                FixedInterestRate_RateofinterestPA = Result['Rate of interest (fixed)']

                # print("url", response.url)
                # # print("VehicleKey", VehicleKey)
                # # print("CarModel", CarModel)
                # print("Products", Result)
                # input("stop")

                item = CarItem()
                item['CarMake'] = 'Skoda'
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                item['TypeofFinance'] = self.get_type_of_finance('PCP')
                item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
                if item['MonthlyPayment']:
                    item['MonthlyPayment'] = float(item['MonthlyPayment'])
                item['CustomerDeposit'] = self.make_two_digit_no(str(CustomerDeposit))
                item['RetailerDepositContribution'] = self.remove_percentage_sign(str(RetailerDepositContribution))
                if item['RetailerDepositContribution']:
                    item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
                item['OnTheRoadPrice'] = self.remove_percentage_sign(str(OnTheRoadPrice))
                if item['OnTheRoadPrice']:
                    item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
                item['OptionalPurchase_FinalPayment'] = self.remove_percentage_sign(str(OptionalPurchase_FinalPayment))
                item['AmountofCredit'] = self.remove_percentage_sign(str(AmountofCredit))
                item['DurationofAgreement'] = self.remove_percentage_sign(str(DurationofAgreement))
                item['TotalAmountPayable'] = self.remove_percentage_sign(str(TotalAmountPayable))
                item['OptionToPurchase_PurchaseActivationFee'] = self.remove_percentage_sign(str(OptionToPurchase_PurchaseActivationFee))
                item['RepresentativeAPR'] = self.remove_percentage_sign(str(RepresentativeAPR))
                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(str(FixedInterestRate_RateofinterestPA))
                item['ExcessMilageCharge'] = self.remove_percentage_sign(str(ExcessMilageCharge))
                item['AverageMilesPerYear'] = '10000'
                item['OfferExpiryDate'] = OfferExpiryDate
                item['DebugMode'] = self.Debug_Mode
                item['RetailCashPrice'] = self.remove_percentage_sign(str(OnTheRoadPrice))
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                item['CarimageURL'] = ''
                item['WebpageURL'] = 'https://finance.skoda-auto.com/210/en-gb/'
                if item['MonthlyPayment'] != '':
                    yield item



    def parse_promotional_url(self, response):
        """
        Promotional cars
        """
        url_path = self.getTexts(response, "//a[contains(text(), 'SEE OFFER')]/@href")
        for href in url_path:
            # print("a: ",href)
            # print("response: ", response.url)
            # input("stop")

            # if "/car-finance/motability" not in url and url != '':
            #     href = "https://www.skoda.co.uk" + url
            yield Request(href, callback=self.parse_promotional_data, headers=self.headers)

    def parse_promotional_data(self, response):
        """
        Promotional cars data
        """

        carDataJson = self.getText(response, '//div[@data-module="table"]/@data-props')
        if carDataJson:
            jsonResult = json.loads(carDataJson)
            Modelcolumns = jsonResult['viewModel']['columns'][0]['title']
            CarModel = Modelcolumns.split("example for")[1].split(",")[0]
            AverageMilesPerYear = Modelcolumns.split('mile agreement')[0].split(", ")[-1].strip()
            DataRow = jsonResult['viewModel']['rows']
            for offer_Data in DataRow:
                Duration = offer_Data['values'][0]['value']
                if "Duration (Months)" in Duration:
                    DurationofAgreement = offer_Data['values'][1]['value']


                Payments = offer_Data['values'][0]['value']
                if "47 monthly \npayments of" in Payments:
                    MonthlyPayment = Payments['47 monthly \npayments of']
                elif "47 monthly payments of" in Payments:
                    MonthlyPayment = Payments['47 monthly payments of']
                elif "48 monthly \npayments of" in data:
                    MonthlyPayment = Payments['48 monthly \npayments of']
                elif "35 monthly payments of" in Payments:
                    MonthlyPayment = Payments['35 monthly payments of']
                elif "35 monthly \npayments of" in data:
                    MonthlyPayment = Payments['35 monthly \npayments of']

                Contribution = offer_Data['values'][0]['value']
                if "ŠKODA Contribution" in Contribution:
                    RetailerDepositContribution = offer_Data['values'][1]['value']
                elif "ŠKODA deposit \ncontribution" in Contribution:
                    RetailerDepositContribution = offer_Data['values'][1]['value']
                elif "'ŠKODA deposit\ncontribution" in Contribution:
                    RetailerDepositContribution = offer_Data['values'][1]['value']


                Deposit = offer_Data['values'][0]['value']
                if "Customer deposit" in Deposit:
                    CustomerDeposit = offer_Data['values'][1]['value']
                elif "Customer Deposit" in Deposit:
                    CustomerDeposit = offer_Data['values'][1]['value']


                OTR = offer_Data['values'][0]['value']
                if "Retail Cash Price \n(inc. Paint)" in OTR:
                    OnTheRoadPrice = offer_Data['values'][1]['value']
                elif "Retail Cash Price\n (inc. Paint)" in OTR:
                    OnTheRoadPrice = offer_Data['values'][1]['value']
                elif "Retail Cash Price (inc. Paint)" in OTR:
                    OnTheRoadPrice = offer_Data['values'][1]['value']

                amount = offer_Data['values'][0]['value']
                if "Amount of credit" in amount:
                    AmountofCredit = offer_Data['values'][1]['value']
                elif "Amount of Credit" in amount:
                    AmountofCredit = offer_Data['values'][1]['value']


                OptionalPayment = offer_Data['values'][0]['value']
                if "Optional final payment" in OptionalPayment:
                    OptionalPurchase_FinalPayment = offer_Data['values'][1]['value']
                elif "Optional Final Payment" in OptionalPayment:
                    OptionalPurchase_FinalPayment = offer_Data['values'][1]['value']
                elif "Optional Final \nPayment " in OptionalPayment:
                    OptionalPurchase_FinalPayment = offer_Data['values'][1]['value']


                payable = offer_Data['values'][0]['value']
                if "Total amount payable" in payable:
                    TotalAmountPayable = offer_Data['values'][1]['value']
                elif "Total Amount Payable" in payable:
                    TotalAmountPayable = offer_Data['values'][1]['value']
                elif "Total Amount \nPayable" in payable:
                    TotalAmountPayable = offer_Data['values'][1]['value']


                Fee = offer_Data['values'][0]['value']
                if "Option to Purchase Fee\n(payable at the end \nof your agreement)" in Fee:
                    OptionToPurchase_PurchaseActivationFee = offer_Data['values'][1]['value']
                elif "Option to purchase fee \n(payable at the end of \nyour agreement)" in Fee:
                    OptionToPurchase_PurchaseActivationFee = offer_Data['values'][1]['value']
                elif "Option to Purchase Fee (Payable at the end of your agreement)" in Fee:
                    OptionToPurchase_PurchaseActivationFee = offer_Data['values'][1]['value']
                elif "Option to Purchase \nFee (Payable at the end\n of your agreement)\n" in Fee:
                    OptionToPurchase_PurchaseActivationFee = offer_Data['values'][1]['value']
                elif "Option to Purchase Fee \n(payable at the end \nof your agreement)" in Fee:
                    OptionToPurchase_PurchaseActivationFee = offer_Data['values'][1]['value']

                interest = offer_Data['values'][0]['value']
                if "Rate of Interest" in interest:
                    FixedInterestRate_RateofinterestPA = offer_Data['values'][1]['value']


                APR = offer_Data['values'][0]['value']
                if "Representative APR" in APR:
                    RepresentativeAPR = offer_Data['values'][1]['value']


                ExMilliage = offer_Data['values'][0]['value']
                if "Excess Mileage" in ExMilliage:
                    ExcessMilageCharge = offer_Data['values'][1]['value']

                    # allText= self.getTextAll(response, '//div[@class="body-wrapper"]/div[@class="body"]//p/sup[contains(text(), "Ordered by")]/text()')
                    # if not allText:
                    #     allText= self.getTextAll(response, '//div[@class="body-wrapper"]/div[@class="body"]//p[contains(text(), "Ordered by")]/text()')
                    # offerExp = allText.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
                    # OfferExpiryDate = self.dateMatcher(offerExp)

                    OfferExpiryDate = '30/06/2022'

                    # print("DataRow: ", allText)
                    # # # # print("ExcessMilageCharge: ",ExcessMilageCharge)
                    # # # # print("RepresentativeAPR: ", RepresentativeAPR)
                    # # # # print("FixedInterestRate_RateofinterestPA: ",FixedInterestRate_RateofinterestPA)
                    # # # # print("TotalAmountPayable: ",TotalAmountPayable)
                    # # # # print("OnTheRoadPrice: ",CustomerDeposit)

                    # if "car-finance/new-enyaq-iv-deals" in response.url:
                    #     print("offer_Data: ",offer_Data)
                    #     print("response: ", response.url)
                    #     input("stop")


                    item = CarItem()
                    item['CarMake'] = 'Skoda'
                    item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                    item['TypeofFinance'] = self.get_type_of_finance('Personal Contract Plan')
                    item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                    # if item['MonthlyPayment']:
                    #     item['MonthlyPayment'] = float(item['MonthlyPayment'])
                    item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                    # if item['CustomerDeposit']:
                    #     item['CustomerDeposit'] = float(item['CustomerDeposit'])
                    item['RetailerDepositContribution'] = self.make_two_digit_no(RetailerDepositContribution)
                    # if item['RetailerDepositContribution']:
                    #     item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
                    item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
                    # if item['OnTheRoadPrice']:
                    #     item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
                    item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
                    item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
                    item['DurationofAgreement'] = DurationofAgreement
                    item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
                    item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(OptionToPurchase_PurchaseActivationFee)
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                    item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
                    item['OfferExpiryDate'] = OfferExpiryDate
                    item['DebugMode'] = self.Debug_Mode
                    item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    try:
                        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    except:
                        item['DepositPercent'] = float()
                    item['CarimageURL'] = ''
                    item['WebpageURL'] = response.url
                    if item['MonthlyPayment'] != '':
                        yield item

        else:

            model = self.getText(response, '//div[@class="headline"]//text()')
            if 'finance offers' in model:
                CarModel = model.split(" finance offers")[0].split("The ")[1]
            # else:
            #     models = self.getText(response, '//tbody/tr/td[contains(text(), "Representative example for")]/following-sibling::td/text()')
            #     carModel = models.split("based on a")[0]
            DataText = self.getText(response, '//div[@class="body-wrapper"]/div[@class="body"]//h4//text()')
            RepresentativeAPR = DataText.split(" APR")[0].strip()
            RetailerDepositContribution = DataText.split(" Deposit Contribution")[0].split("£")[1].strip()
            if "^ across" in DataText:
                MonthlyPayment = DataText.split("^ across")[0].split("for £")[1]
            elif "per month" in DataText:
                try:
                    MonthlyPayment = DataText.split("per month")[0].split("From ")[1]
                except:
                    MonthlyPayment = DataText.split("per month")[0].split("from")[1]

            # # print("DataText: ",DataText)
            # # print("Representative: ",Representative)
            # # print("RetailerDepositContribution: ",RetailerDepositContribution)
            # # print("MonthlyPayment: ",MonthlyPayment)
            # # print("carModel: ",carModel)
            # # print("response: ", response.url)
            # # input("stop")
            #

            allText= self.getTextAll(response, '//div[@class="body-wrapper"]/div[@class="body"]//p/sup[contains(text(), "Ordered by")]/text()')
            if not allText:
                allText= self.getTextAll(response, '//div[@class="body-wrapper"]/div[@class="body"]//p[contains(text(), "Ordered by")]/text()')
            offerExp = allText.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
            OfferExpiryDate = self.dateMatcher(offerExp)[1]

            # if "Ordered by" in allText:
            #     OfferExpiryDate = allText.split("Ordered by")[1].split("and")[0]
            # else:
            #     OfferExpiryDate = 'N/A'
            # print("allText: ", OfferExpiryDate)
            # print("response: ", response.url)
            # input("stop")

            item = CarItem()
            item['CarMake'] = 'Skoda'
            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
            item['TypeofFinance'] = self.get_type_of_finance('Personal Contract Plan')
            item['MonthlyPayment'] = MonthlyPayment
            # if item['MonthlyPayment']:
            #     item['MonthlyPayment'] = float(item['MonthlyPayment'])
            item['CustomerDeposit'] = 'N/A'
            # if item['CustomerDeposit']:
            #     item['CustomerDeposit'] = float(item['CustomerDeposit'])
            item['RetailerDepositContribution'] = RetailerDepositContribution
            # if item['RetailerDepositContribution']:
            #     item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
            item['OnTheRoadPrice'] = 'N/A'
            # if item['OnTheRoadPrice']:
            #     item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = '36'
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = RepresentativeAPR
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = 'N/A'
            item['OfferExpiryDate'] = OfferExpiryDate
            item['DebugMode'] = self.Debug_Mode
            item['RetailCashPrice'] = 'N/A'
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            item['CarimageURL'] = ''
            item['WebpageURL'] = response.url
            if item['MonthlyPayment'] != '':
                yield item
