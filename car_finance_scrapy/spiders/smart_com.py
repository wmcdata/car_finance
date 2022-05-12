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


### NEW SPIDER 01-10-2019 ###HM

class SmartSpider(BaseSpider):
    name = "smart.com"
    allowed_domains = []
    holder = list()
    start_url = 'https://www.smart.com/gb/en/offers-overview'
    base_url = 'https://www.smart.com/'

    def __init__(self):
        super(SmartSpider, self).__init__()
        self.i = 0

    def start_requests(self):
        """ Start request for Cars
        """
        # url = 'https://shop.mercedes-benz.co.uk/new/results'
        yield Request(self.start_url, callback=self.parse_new_offers_data, headers=self.headers, dont_filter=True)

    def parse_new_offers_data(self, response):
        """ NEW OFFERS MULTIPLE MODELS ID
        """
        # print("resp", response.url)
        # # print("href", href)
        # input("stop")
        # linkloop = self.getText(response, '//ul[@class="interactions__buttonList"]/li/a/@href')
        # checkForModelId = response.url
        # if "ModelId=" in checkForModelId:
        modeldata = ['100', '101', '102']
        for modelId in modeldata:
            # print("resp", response.url)
            # print("modelId/", modelId)
            # input("stop")
            import requests
            duration = ['24','36','48']
            for duration_no in duration:
                if "48" in duration_no:
                    url = "https://stock-api.mercedes-benz.co.uk/search/new"
                    payload = '{"Criteria":{"ModelId":['+modelId+'],"pid":{"Values":[null]},"PreviousModel":false,"LatestModel":true},"Sort":{"Id":1},"FinanceCriteria":{"Key":"PCP","Name":"Agility (Personal Contract Plan)","Type":"PCP","IsDefault":true,"Term":{"Options":[{"IsDefault":false,"Value":24},{"IsDefault":false,"Value":36},{"IsDefault":true,"Value":48}]},"Deposit":{"Default":"17.5%"},"Mileage":{"Options":[{"IsDefault":true,"Value":10000},{"IsDefault":false,"Value":12000},{"IsDefault":false,"Value":14000},{"IsDefault":false,"Value":16000},{"IsDefault":false,"Value":18000},{"IsDefault":false,"Value":20000},{"IsDefault":false,"Value":22000},{"IsDefault":false,"Value":24000},{"IsDefault":false,"Value":26000},{"IsDefault":false,"Value":28000},{"IsDefault":false,"Value":30000},{"IsDefault":false,"Value":32000},{"IsDefault":false,"Value":34000},{"IsDefault":false,"Value":36000},{"IsDefault":false,"Value":38000},{"IsDefault":false,"Value":40000}]},"MonthlyPrice":{"Min":50,"Max":4000},"IsPersonalised":false,"CustomerType":"Personal","VehicleType":"UNASSIGNED"},"Paging":{"ResultsPerPage":20,"PageIndex":0},"BestMatchCriteriaId":"6A9BCA02-BD6C-4854-ABAB-3560FC2CDB70"}'
                elif "36" in duration_no:
                    url = "https://stock-api.mercedes-benz.co.uk/search/new"
                    payload = '{"Criteria":{"ModelId":['+modelId+'],"pid":{"Values":[null]},"PreviousModel":false,"LatestModel":true},"Sort":{"Id":1},"FinanceCriteria":{"Key":"PCP","Name":"Agility (Personal Contract Plan)","Type":"PCP","IsDefault":true,"Term":{"Options":[{"IsDefault":false,"Value":24},{"IsDefault":true,"Value":36},{"IsDefault":false,"Value":48}]},"Deposit":{"Default":"17.5%"},"Mileage":{"Options":[{"IsDefault":true,"Value":10000},{"IsDefault":false,"Value":12000},{"IsDefault":false,"Value":14000},{"IsDefault":false,"Value":16000},{"IsDefault":false,"Value":18000},{"IsDefault":false,"Value":20000},{"IsDefault":false,"Value":22000},{"IsDefault":false,"Value":24000},{"IsDefault":false,"Value":26000},{"IsDefault":false,"Value":28000},{"IsDefault":false,"Value":30000},{"IsDefault":false,"Value":32000},{"IsDefault":false,"Value":34000},{"IsDefault":false,"Value":36000},{"IsDefault":false,"Value":38000},{"IsDefault":false,"Value":40000}]},"MonthlyPrice":{"Min":50,"Max":4000},"IsPersonalised":false,"CustomerType":"Personal","VehicleType":"UNASSIGNED"},"Paging":{"ResultsPerPage":20,"PageIndex":0},"BestMatchCriteriaId":"6A9BCA02-BD6C-4854-ABAB-3560FC2CDB70"}'
                elif "24" in duration_no:
                    url = "https://stock-api.mercedes-benz.co.uk/search/new"
                    payload = '{"Criteria":{"ModelId":['+modelId+'],"pid":{"Values":[null]},"PreviousModel":false,"LatestModel":true},"Sort":{"Id":1},"FinanceCriteria":{"Key":"PCP","Name":"Agility (Personal Contract Plan)","Type":"PCP","IsDefault":true,"Term":{"Options":[{"IsDefault":true,"Value":24},{"IsDefault":true,"Value":36},{"IsDefault":false,"Value":48}]},"Deposit":{"Default":"17.5%"},"Mileage":{"Options":[{"IsDefault":true,"Value":10000},{"IsDefault":false,"Value":12000},{"IsDefault":false,"Value":14000},{"IsDefault":false,"Value":16000},{"IsDefault":false,"Value":18000},{"IsDefault":false,"Value":20000},{"IsDefault":false,"Value":22000},{"IsDefault":false,"Value":24000},{"IsDefault":false,"Value":26000},{"IsDefault":false,"Value":28000},{"IsDefault":false,"Value":30000},{"IsDefault":false,"Value":32000},{"IsDefault":false,"Value":34000},{"IsDefault":false,"Value":36000},{"IsDefault":false,"Value":38000},{"IsDefault":false,"Value":40000}]},"MonthlyPrice":{"Min":50,"Max":4000},"IsPersonalised":false,"CustomerType":"Personal","VehicleType":"UNASSIGNED"},"Paging":{"ResultsPerPage":20,"PageIndex":0},"BestMatchCriteriaId":"6A9BCA02-BD6C-4854-ABAB-3560FC2CDB70"}'

                # payload = '{"Criteria":{"ModelId":['+modelId+'],"PreviousModel":false,"LatestModel":false},"Sort":{"Id":1},"FinanceCriteria":{"Key":"PCH","Name":"Personal Contract Hire","Type":"PCH","IsDefault":false,"Term":{"Options":[{"IsDefault":false,"Value":24},{"IsDefault":false,"Value":36},{"IsDefault":true,"Value":48}]},"Deposit":{"Default":"17.5%"},"Mileage":{"Options":[{"IsDefault":false,"Value":6000},{"IsDefault":false,"Value":7000},{"IsDefault":false,"Value":8000},{"IsDefault":false,"Value":9000},{"IsDefault":true,"Value":10000},{"IsDefault":false,"Value":12000},{"IsDefault":false,"Value":14000},{"IsDefault":false,"Value":16000},{"IsDefault":false,"Value":18000},{"IsDefault":false,"Value":20000},{"IsDefault":false,"Value":22000},{"IsDefault":false,"Value":24000},{"IsDefault":false,"Value":26000},{"IsDefault":false,"Value":28000},{"IsDefault":false,"Value":30000},{"IsDefault":false,"Value":32000},{"IsDefault":false,"Value":34000},{"IsDefault":false,"Value":36000},{"IsDefault":false,"Value":38000},{"IsDefault":false,"Value":40000}]},"MonthlyPrice":{"Min":50,"Max":3000},"IsPersonalised":true,"CustomerType":"Personal","VehicleType":"UNASSIGNED","AdvanceRentals":{"Options":[{"IsDefault":false,"Value":1},{"IsDefault":false,"Value":3},{"IsDefault":false,"Value":6},{"IsDefault":true,"Value":9}]}},"Paging":{"ResultsPerPage":20,"PageIndex":0},"BestMatchCriteriaId":"6A9BCA02-BD6C-4854-ABAB-3560FC2CDB70"}'
                headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9maWxlSUQiOiI1ZWE2YzA3ZDMwM2U0OWZhOGZhMjFkMDk5YTczN2MzMCIsImlhdCI6MTY0NjY1MTI3NzU4MywiZXhwIjoxNjQ2NjUyMTc3NTgzfQ.eR2i-Lv0hGCWJG-9afYwVjD7GS9GXre_CDmKXNFkBS5nwc3iqazWJPkaK_ETwRAokGEz3TY5jzqKd-oc8QX49XbdnvS2PzKL8HbW9UG16t53rfe2vBsNFZ3Jl4imryMIGLeTHSUchx2HHZ67iUUmBpw_DAGVf_y3Jg8BgGnBrRu0_iudfTys5GRtCE7wZZsx8S_lsurtHmCDBvk9vRqJuxPCHpwoG3HigO_5qxh_djiPMkJlQH4QC2_O-IDMwJKePtB32D1jzcBPDgv8MIGR8_gzJBC5FEcGOuoMgtz9vySmUOiKmJUDF4gZt-TWLiqfpeb2LpNfYCbpFRHibW7oJQ',
                'content-type': 'application/json',
                'origin': 'https://shop.mercedes-benz.co.uk',
                'referer': 'https://shop.mercedes-benz.co.uk/',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                'Cookie': 'osp_session=vfpBQJXgp9tNy4tvHY0GqjgrzNSCYGaDBaio4Fp0'
                }

                response_data = requests.request("POST", url, data=payload, headers=headers)
                json_data = json.loads(response_data.text)
                if "SearchResults" in json_data:
                    SearchResults = json_data['SearchResults']
                    Vehicles = SearchResults['Vehicles']
                    if Vehicles != []:

                    

                        # offerExpiredDate = Vehicles[0]['FinanceQuote']['ValidTo']

                        # print("url", response.url)
                        # print("offerExpiredDate: ", offerExpiredDate)
                        # input("stop")
                        # offerExpiredDate = datetime.strptime(Content, "%Y-%m-%d").strftime('%d/%m/%Y')
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
                        if "QuoteDto" in SearchResults['Vehicles'][0]:
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



                            car_make = "Smart"
                            item = CarItem()
                            item['CarMake'] = car_make
                            item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance) ### PCP
                            item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
                            item['CustomerDeposit'] = self.make_two_digit_no(str(CustomerDeposit))
                            item['RetailerDepositContribution'] = '1000'
                            item['OnTheRoadPrice'] = OnTheRoadPrice
                            item['AmountofCredit'] = AmountOfCredit
                            item['DurationofAgreement']   = self.remove_percentage_sign(str(DurationOfAgreement))
                            item['OptionalPurchase_FinalPayment']   = OptionalPurchasePayment
                            item['TotalAmountPayable'] = TotalAmountPayable
                            item['OptionToPurchase_PurchaseActivationFee'] =  self.remove_percentage_sign(str(PurchaseActivationFee))
                            item['RepresentativeAPR'] =  self.remove_percentage_sign(APR)
                            item['FixedInterestRate_RateofinterestPA'] =  self.remove_percentage_sign(FixedInterestRate)
                            item['ExcessMilageCharge'] =  self.remove_percentage_sign(str(ExcessMileageCharge))
                            item['AverageMilesPerYear'] =  self.remove_percentage_sign(AnnualMileage)
                            item['RetailCashPrice'] = OnTheRoadPrice
                            item['OfferExpiryDate'] = '30/06/2022'
                            item['WebpageURL'] = WebpageURL
                            item['CarimageURL'] = CarImageUrl
                            item['DebugMode'] = self.Debug_Mode
                            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                            try:
                                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                            except:
                                item['DepositPercent'] = float()
                            yield item

                    # print("url", response.url)
                    # print("json_data: ", json_data)
                    # input("stop")
