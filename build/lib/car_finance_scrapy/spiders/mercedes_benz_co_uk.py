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

### Headers need to update for FIX
class MercedesSpider(BaseSpider):
    unique_data = set()
    name = "mercedes-benz.co.uk" ### PCP CARS
    allowed_domains = []
    holder = list()
    # start_url = ['https://stock.mercedes-benz.co.uk/used/search-results', 'https://www.mercedes-benz.co.uk/passengercars/buy/new-offers.html']
    start_url = 'https://www.mercedes-benz.co.uk/passengercars/buy/new-offers/eqv-offer.module.html'
    base_url = 'https://www.mercedes-benz.co.uk'


# https://www.mercedes-benz.co.uk/passengercars.html?group=all&subgroup=see-all&view=BODYTYPE
    def __init__(self):
        super(MercedesSpider, self).__init__()
        self.i = 0
        #self.XPATH_CATEGORY_LEVEL_1 = '//div[@id="car-range"]//div[@id="model-range"]/ul/li'

        # 'https://stock.mercedes-benz.co.uk/used/search-results'
        ### New Code ###

        ### Full code cars
        ### '{"Criteria":{"FuelId":{"Id":"FuelId","Values":[2,4,3,1]},"OTR":{"Min":23550,"Max":313116},"RetailPrice":{"Min":23550,"Max":313116},"ModelId":[1,2,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21,23,24,25,26,27,28,29,30,31,78,76,80,89],"TransmissionId":{"Id":"TransmissionId","Values":[1,2]}},"Sort":{"Id":null},"ExcludeSearchResults":false,"BestMatchCriteriaId":"6A9BCA02-BD6C-4854-ABAB-3560FC2CDB70","FinanceCriteria":{"Key":"PCP","Name":"Agility (Personal Contract Plan)","Type":"PCP","IsDefault":true,"Term":{"Options":[{"IsDefault":false,"Value":24},{"IsDefault":false,"Value":36},{"IsDefault":true,"Value":48}]},"Deposit":{"Default":"17.5%"},"Mileage":{"Options":[{"IsDefault":true,"Value":10000},{"IsDefault":false,"Value":12000},{"IsDefault":false,"Value":14000},{"IsDefault":false,"Value":16000},{"IsDefault":false,"Value":18000},{"IsDefault":false,"Value":20000},{"IsDefault":false,"Value":22000},{"IsDefault":false,"Value":24000},{"IsDefault":false,"Value":26000},{"IsDefault":false,"Value":28000},{"IsDefault":false,"Value":30000},{"IsDefault":false,"Value":32000},{"IsDefault":false,"Value":34000},{"IsDefault":false,"Value":36000},{"IsDefault":false,"Value":38000},{"IsDefault":false,"Value":40000}]},"MonthlyPrice":{"Min":50,"Max":3176},"IsPersonalised":true,"CustomerType":"Personal","VehicleType":"UNASSIGNED","agilitySelected":true,"MonthlyPriceRange":{"financeMinRange":50,"financeMaxRange":4000},"RegularPayment":""},"SessionId":null}'

    def start_requests(self):
        yield Request(self.start_url, callback=self.parse_new_offers_url, headers=self.headers)

    def parse_new_offers_url(self, response):
        """ NEW OFFERS MULTIPLE MODELS
        """
        # urlList = response.xpath('//article[@class="aem--grid-cp moduleassembler__module  "]/@data-aem-moduletrackingname')
        # for url in urlList:
        #     data = url.xpath('//div[@class="swipeableteaser__base"]//div[@class="swipeableteaser__slide "]')
        #      = self.getText(data, './/')
        urlList = self.getTexts(response, '//ul/li[@class="interactions__ctaitem"]/a[contains(@class, "interactions__ctalink interactions__ctalink") or contains(@class, "interactions__ctalink interactions__ctalink--primary")]/@href')
        for url in urlList:
            href = urljoin(response.url, url)
            # print("resp", response.url)
            # print("href", href)
            # input("stop")
            yield Request(href, callback=self.parse_new_offers_data, headers=self.headers)


    def parse_new_offers_data(self, response):
        """ NEW OFFERS MULTIPLE MODELS ID
        """
        # print("resp", response.url)
        # # print("href", href)
        # input("stop")
        # linkloop = self.getText(response, '//ul[@class="interactions__buttonList"]/li/a/@href')

 

        checkForModelId = response.url
        if "ModelId=" in checkForModelId:
            modelId = checkForModelId.split("ModelId=")[1].split("&")[0]
            if modelId and (modelId not in self.unique_data):
                self.unique_data.add(modelId)
                import requests

                url = "https://shop-m-api.mercedes-benz.co.uk/v1/vehicles/search/new"
                payload = '{"Criteria":{"ModelId":['+modelId+'],"pid":{"Values":[null]},"PreviousModel":false,"LatestModel":true},"Sort":{"Id":1},"FinanceCriteria":{"Key":"PCP","Name":"Agility (Personal Contract Plan)","Type":"PCP","IsDefault":true,"Term":{"Options":[{"IsDefault":false,"Value":24},{"IsDefault":false,"Value":36},{"IsDefault":true,"Value":48}]},"Deposit":{"Default":"17.5%"},"Mileage":{"Options":[{"IsDefault":true,"Value":10000},{"IsDefault":false,"Value":12000},{"IsDefault":false,"Value":14000},{"IsDefault":false,"Value":16000},{"IsDefault":false,"Value":18000},{"IsDefault":false,"Value":20000},{"IsDefault":false,"Value":22000},{"IsDefault":false,"Value":24000},{"IsDefault":false,"Value":26000},{"IsDefault":false,"Value":28000},{"IsDefault":false,"Value":30000},{"IsDefault":false,"Value":32000},{"IsDefault":false,"Value":34000},{"IsDefault":false,"Value":36000},{"IsDefault":false,"Value":38000},{"IsDefault":false,"Value":40000}]},"MonthlyPrice":{"Min":50,"Max":4000},"IsPersonalised":false,"CustomerType":"Personal","VehicleType":"UNASSIGNED"},"Paging":{"ResultsPerPage":20,"PageIndex":0},"BestMatchCriteriaId":"6A9BCA02-BD6C-4854-ABAB-3560FC2CDB70"}'

                # print("payload", payload)
                # input("stop")
                # payload = "{\"Criteria\":{\"ModelId\":["+modelId+"],\"PreviousModel\":false,\"LatestModel\":false},\"Sort\":{\"Id\":1},\"FinanceCriteria\":{\"Key\":\"PCP\",\"Name\":\"Agility (Personal Contract Plan)\",\"Type\":\"PCP\",\"IsDefault\":true,\"Term\":{\"Options\":[{\"IsDefault\":false,\"Value\":24},{\"IsDefault\":false,\"Value\":36},{\"IsDefault\":true,\"Value\":48}]},\"Deposit\":{\"Default\":\"17.5%\"},\"Mileage\":{\"Options\":[{\"IsDefault\":true,\"Value\":10000},{\"IsDefault\":false,\"Value\":12000},{\"IsDefault\":false,\"Value\":14000},{\"IsDefault\":false,\"Value\":16000},{\"IsDefault\":false,\"Value\":18000},{\"IsDefault\":false,\"Value\":20000},{\"IsDefault\":false,\"Value\":22000},{\"IsDefault\":false,\"Value\":24000},{\"IsDefault\":false,\"Value\":26000},{\"IsDefault\":false,\"Value\":28000},{\"IsDefault\":false,\"Value\":30000},{\"IsDefault\":false,\"Value\":32000},{\"IsDefault\":false,\"Value\":34000},{\"IsDefault\":false,\"Value\":36000},{\"IsDefault\":false,\"Value\":38000},{\"IsDefault\":false,\"Value\":40000}]},\"MonthlyPrice\":{\"Min\":50,\"Max\":4000},\"IsPersonalised\":false,\"CustomerType\":\"Personal\",\"VehicleType\":\"UNASSIGNED\"},\"Paging\":{\"ResultsPerPage\":20,\"PageIndex\":0},\"BestMatchCriteriaId\":\"6A9BCA02-BD6C-4854-ABAB-3560FC2CDB70\"}"
                
            
                headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9maWxlSUQiOiI1ZWE2YzA3ZDMwM2U0OWZhOGZhMjFkMDk5YTczN2MzMCIsImlhdCI6MTY1MTg4MjgwMTU1NywiZXhwIjoxNjUxODgzNzAxNTU3fQ.XFsF6fCvilV5kAEvFZqld5Bfed-wKwHv5vbnFestjNafC2FMYJTxAAZ9lcKQDag3-SGeQeyPAOazM-CjCIfIJbpZX2jJSx1OxUz01Kkurkty22o4fO9fXbYqVqp6RT9Rp1CjJyCTsJtUzUicg1wwAdQlun5iEVYjLDmgcRyEw_xMvSc4CsFYzcV66vsDFKjf3TFRAgrubBAof-326cHrHGTSureFwPz5ouqEqqAvew2d_k3UjH-2fiBxK1EGttZlXgoGD09RcJTsQeJgPFBK7J_Cc7ta-7f2Jt8FgYGZfHyq2kmSEbJDGt2k09Drg6j39JbCG7hw_80AyjPPZPrTjw',
                'content-type': 'application/json',
                'origin': 'https://shop.mercedes-benz.co.uk',
                'referer': 'https://shop.mercedes-benz.co.uk/',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
                'Cookie': 'osp_session=PIcTKd1KIOTS2PK4DMpvIkBaUqej1YiBtukUHPxp'
                }
                
                response_data = requests.request("POST", url, data=payload, headers=headers)
                json_data = json.loads(response_data.text)
                SearchResults = json_data['SearchResults']
                Vehicles = SearchResults['Vehicles']
                # print("veh", json_data)
                # input("stop")
                if Vehicles != []:
                    if "OfferExpiryDate" in SearchResults['Vehicles'][0]:
                        offerExp = SearchResults['Vehicles'][0]['OfferExpiryDate']
                        OfferExpiryDate = datetime.strptime(offerExp, "%Y-%m-%d").strftime('%d/%m/%Y')
                    else:
                        OfferExpiryDate = 'N/A'
                    CarImageUrl = Vehicles[0]['Media']['MainImageUrl']
                    if not CarImageUrl:
                        CarImageUrl = Vehicles[1]['Media']['MainImageUrl']

                    Model = Vehicles[0]['Model'].lower()
                    Vin = Vehicles[0]['Vin']
                    Retailer_id = Vehicles[0]['Retailer']['Id']

                    Description =  Vehicles[0]['Description']
                    Modelname =  Vehicles[0]['Model']
                    BodyStyle =  Vehicles[0]['BodyStyle']
                    # CarModel = Description+' '+ Modelname +' '+ BodyStyle
                    CarModel = Description

                    WebpageURL = 'https://stock.mercedes-benz.co.uk/vehicle-details/'+Model+'/'+str(Vin)+'/'+str(Retailer_id)

                    QuoteData = SearchResults['Vehicles'][0]['QuoteDto']
                    if "MonthlyPayment" in QuoteData: ### IF data is not available on Index 0
                        MonthlyPayment = QuoteData['MonthlyPayment']
                        OnTheRoadPrice = QuoteData['OTR']
                        CustomerDeposit = QuoteData['CustomerDeposit']
                        AmountOfCredit = QuoteData['AmountOfCredit']
                        OptionalPurchasePayment = QuoteData['OptionalPurchasePayment']
                        TotalAmountPayable = QuoteData['TotalAmountPayable']
                        PurchaseActivationFee = QuoteData['PurchaseActivationFee']
                        DurationOfAgreement = QuoteData['DurationOfAgreement']
                        AnnualMileage = QuoteData['AnnualMileage']
                        ExcessMileageCharge = QuoteData['ExcessMileageCharge']
                        FixedInterestRate = QuoteData['FixedInterestRate']
                        APR = QuoteData['APR']
                        TypeofFinance = QuoteData['Product']
                    else: ### on index 1
                        QuoteData = SearchResults['Vehicles'][1]['QuoteDto']
                        MonthlyPayment = QuoteData['MonthlyPayment']
                        OnTheRoadPrice = QuoteData['OTR']
                        CustomerDeposit = QuoteData['CustomerDeposit']
                        AmountOfCredit = QuoteData['AmountOfCredit']
                        OptionalPurchasePayment = QuoteData['OptionalPurchasePayment']
                        TotalAmountPayable = QuoteData['TotalAmountPayable']
                        PurchaseActivationFee = QuoteData['PurchaseActivationFee']
                        DurationOfAgreement = QuoteData['DurationOfAgreement']
                        AnnualMileage = QuoteData['AnnualMileage']
                        ExcessMileageCharge = QuoteData['ExcessMileageCharge']
                        FixedInterestRate = QuoteData['FixedInterestRate']
                        APR = QuoteData['APR']
                        TypeofFinance = QuoteData['Product']



                    car_make = "Mercedes-Benz"
                    item = CarItem()
                    item['CarMake'] = car_make
                    item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                    item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance) ### PCP
                    item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
                    item['CustomerDeposit'] = self.make_two_digit_no(str(CustomerDeposit))
                    item['RetailerDepositContribution'] = 'N/A'
                    item['OnTheRoadPrice'] = OnTheRoadPrice
                    item['AmountofCredit'] = AmountOfCredit
                    item['DurationofAgreement']   = self.remove_percentage_sign(str(DurationOfAgreement))
                    item['OptionalPurchase_FinalPayment']   = OptionalPurchasePayment
                    item['TotalAmountPayable'] = TotalAmountPayable
                    item['OptionToPurchase_PurchaseActivationFee'] = PurchaseActivationFee
                    item['RepresentativeAPR'] = self.remove_percentage_sign(APR)
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate)
                    item['ExcessMilageCharge'] = self.remove_percentage_sign(str(ExcessMileageCharge))
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage)
                    item['RetailCashPrice'] = OnTheRoadPrice
                    item['OfferExpiryDate'] = OfferExpiryDate ### "10/01/2022"
                    item['WebpageURL'] = WebpageURL
                    item['CarimageURL'] = CarImageUrl
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    try:
                        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    except:
                        item['DepositPercent'] = float()
                    if item['MonthlyPayment'] != "":  
                        yield item


                # print("CarModel", CarModel)
                # print("OfferExpiryDate", WebpageURL)
                # input("stop")
