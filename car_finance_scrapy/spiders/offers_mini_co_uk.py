# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
# from scrapy import log
import urllib
import xmltodict, json
from datetime import datetime, timedelta
from time import gmtime, strftime
from dateutil.relativedelta import relativedelta
import re
from urllib.parse import urljoin
from html.parser import HTMLParser
from requests import Session

class CarFinanceItem(BaseSpider):
    name = "offers.mini.co.uk"

    allowed_domains = []
    holder = list()
    base_url  = 'https://offers.mini.co.uk/'
    start_url = ['https://www.mini.co.uk/en_GB/home/finance-and-insurance/offers.html', 'https://www.minibusinesspartnership.co.uk/umbraco/api/offers/getoffers?brand=1406']

    def __init__(self):
        super(CarFinanceItem, self).__init__()

    def start_requests(self):
        """ Start request
        """
        for url in self.start_url:
            if "finance-and-insurance" in url:
                yield Request(url, callback=self.parse_links, headers=self.headers)
            # else:
            #     yield Request(url, callback=self.parse_pch_link, headers=self.headers)

    def parse_links(self, response):
        """ start_urls
        """
        # pcp = 'https://services.codeweavers.net/api/v2/offers?Referrer=https:%2F%2Foffers.mini.co.uk%2F&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW&AnnualMileage=&ProductFamily=HP&CashDeposit=&Term=48'

        pcp = 'https://services.codeweavers.net/api/v2/offers?AnnualMileage=10000&CashDeposit=&ProductFamily=PCP&Referrer=https:%2F%2Foffers.mini.co.uk%2F&RegularPayment=&SearchIdentifier=3&Term=48&Text=%27derivativesubset:IVS_MINI%27+MINI&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW'
        hp = 'https://services.codeweavers.net/api/v2/offers?AnnualMileage=10000&CashDeposit=&ProductFamily=HP&Referrer=https:%2F%2Foffers.mini.co.uk%2F&RegularPayment=&SearchIdentifier=4&Term=48&Text=%27derivativesubset:IVS_MINI%27+MINI&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW'
        pch = 'https://services.codeweavers.net/api/v2/offers?AnnualMileage=10000&CashDeposit=&ProductFamily=PCH&Referrer=https:%2F%2Foffers.mini.co.uk%2F&RegularPayment=&SearchIdentifier=5&Term=48&Text=%27derivativesubset:IVS_MINI%27+MINI&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW'
        
        # pcp = 'https://services.codeweavers.net/api/v2/offers?AnnualMileage=10000&CashDeposit=&ProductFamily=PCP&Referrer=https:%2F%2Foffers.mini.co.uk%2Foffers%2F06ea4d20-16f5-4b5d-98f0-0791af4a05c4&RegularPayment=&SearchIdentifier=1&Term=48&Text=%27derivativesubset:IVS_MINI%27+MINI&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW'
        # hp = 'https://services.codeweavers.net/api/v2/offers?AnnualMileage=10000&CashDeposit=&ProductFamily=HP&Referrer=https:%2F%2Foffers.mini.co.uk%2Foffers%2F06ea4d20-16f5-4b5d-98f0-0791af4a05c4&RegularPayment=&SearchIdentifier=1&Term=48&Text=%27derivativesubset:IVS_MINI%27+MINI&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW'
        # pch = 'https://services.codeweavers.net/api/v2/offers?AnnualMileage=10000&CashDeposit=&ProductFamily=PCH&Referrer=https:%2F%2Foffers.mini.co.uk%2Foffers%2F06ea4d20-16f5-4b5d-98f0-0791af4a05c4&RegularPayment=&SearchIdentifier=1&Term=48&Text=%27derivativesubset:IVS_MINI%27+MINI&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW'
        
        car_arr = [pcp,hp,pch]
        for arr in car_arr:
            yield Request(arr, callback=self.parse_car_links, headers=self.headers)

    def parse_pch_link(self, response):
        """ BCH OFFERS
        """
        jsondata = json.loads(response.body)
        # print("jsondata", jsondata)
        # input("wait")
        data = jsondata['data']
        for offers in data:
            carModel = offers['name']
            CarimageURL = offers['image']['url']
            WebpageURL = urljoin(response.url, offers['url'])
            DurationofAgreement = offers['rate']['followedBy']
            AnnualMileage = offers['rate']['annualMileage']
            standardOffer = offers['rate']['standard']
            CustomerDeposit = standardOffer['deposit']
            MonthlyPayment = standardOffer['totalRentalRounded']
            ExcessMilageCharge = standardOffer['excessPPM']

            TypeofFinance = 'Business Contract Hire'
            carMake = 'Mini'
            item = CarItem()
            item['CarMake'] = carMake
            item['CarModel'] = self.remove_special_char_on_excel(carModel)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = self.make_two_digit_no(str(MonthlyPayment))
            item['CustomerDeposit'] = self.make_two_digit_no(str(CustomerDeposit))
            item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['DurationofAgreement'] = self.remove_percentage_sign(str(DurationofAgreement))
            item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
            item['RepresentativeAPR'] = 'N/A'
            item['AverageMilesPerYear'] = self.remove_percentage_sign(str(AnnualMileage))
            item['OfferExpiryDate'] = '30/06/2022'
            item['RetailCashPrice'] = 'N/A'
            item['CarimageURL'] = CarimageURL
            item['AmountofCredit'] = 'N/A'
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['ExcessMilageCharge'] = self.remove_percentage_sign(str(ExcessMilageCharge))
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['TotalAmountPayable'] = 'N/A'
            item['WebpageURL'] = WebpageURL
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            yield item

            # print("jsondata", offers)
            # input("wait")

    def parse_car_links(self, response):
        """ start_urls
        """

        data_json = response.body
      
        # xml_data = xmltodict.parse(data_json) ### XML TO JSON
        # data_json = json.dumps(xml_data) ### Full Json/DATA
        data_json = json.loads(data_json) ### Making Dictionary here
        # print("data_json", data_json)
        # print("respo", response.url)
        # input("stop")
        data = data_json['Offers']

        for all_data in data:
            # print("all_data", all_data)
            # print("respo", response.url)
            # input("stop")
            QuoteReference = all_data['Quote']['QuoteReference']
            car_image = all_data['Images']['Banner']
            carModel = all_data['OfferTitle']
            offerCode = all_data['OfferCode']
            AnnualMileage = all_data['Quote']['AnnualMileage']
            CustomerDeposit = all_data['Quote']['CashDeposit']
            MonthlyPayment = all_data['Quote']['RegularPayment']
            RepresentativeAPR = all_data['Quote']['Apr']
            OnTheRoadPrice = all_data['Quote']['OnTheRoadPrice']
            Term = all_data['Quote']['Term']
            ContentExp = all_data['ValidTo'].split("T")[0]
            OfferExpiryDate = datetime.strptime(ContentExp, "%Y-%m-%d").strftime('%d/%m/%Y')
            # offerExp = ContentExp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
            # OfferExpiryDate = self.dateMatcher(offerExp)[1]

            # response_link = 'https://offers.mini.co.uk/offers/' + offerCode

            TypeofFinance = all_data['Quote']['ProductFamily']

            # print("ContentExp", OfferExpiryDate)
            # # print("TypeofFinance", TypeofFinance)
            # # print("TypeofFinance", self.get_type_of_finance(TypeofFinance))
            # print("uirl", response.url)
            # input("wait")

            # if "HP" and "PCP" in TypeofFinance:
            #     DepositContribution = all_data['Quote']['DepositContributions']['Offer.OfferQuote.DepositContribution']['Amount']
            # else:
            #     DepositContribution = 'N/A'

            if "HP" in TypeofFinance or "PCP" in TypeofFinance or "PCH" in TypeofFinance:
                DepositContribution = all_data['Quote']['TotalContribution']
            else:
                DepositContribution = 'N/A'

            WebpageURL = 'https://www.mini.co.uk/en_GB/home/finance-and-insurance/offers.html?=#details#'+str(offerCode)+'::{%22term%22:48,%22product%22:%22'+str(TypeofFinance)+'%22,%22mileage%22:10000,%22deposit%22:'+str(CustomerDeposit)+'}'
            
            # WebpageURL = 'https://www.mini.co.uk/en_GB/home/finance-and-insurance/offers.html#details#'+str(offerCode)+'::{"term":48,"product":"PCP","mileage":10000,"deposit":'+str(CustomerDeposit)+',"sorting":{"id":"PAYMENT_ASC","name":"Lowest price"},"selectedFilters":{"models":[{"name":"3-DOOR HATCH","id":"3-DOOR","selected":false},{"name":"5-DOOR HATCH","id":"5-DOOR","selected":true},{"name":"CONVERTIBLE","id":"CONVERTIBLE","selected":false},{"name":"CLUBMAN","id":"CLUBMAN","selected":false},{"name":"COUNTRYMAN","id":"COUNTRYMAN","selected":false},{"name":"ELECTRIC","id":"MINI ELECTRIC","selected":false},{"name":"PLUG-IN HYBRID","id":"HYBRID","selected":false},{"name":"John Cooper Works","id":"JCW","selected":false}],"transmission":[{"name":"Automatic","id":"Automatic","selected":false,"number":0,"disabled":true},{"name":"Manual","id":"Manual","selected":false,"number":0,"disabled":true},{"name":"Sport","id":"Sport","selected":false,"number":0,"disabled":true}],"fuelType":[{"name":"Petrol","id":"Petrol","selected":false,"number":0,"disabled":true},{"name":"Hybrid","id":"Hybrid Petrol/Electric Plug-in","selected":false,"number":0,"disabled":true},{"name":"Diesel","id":"Diesel","selected":false,"number":0,"disabled":true},{"name":"Electric","id":"Electric","selected":false,"number":0,"disabled":true}],"style":[{"name":"Classic","id":"CL","selected":false,"number":0,"disabled":true},{"name":"Sport","id":"SP","selected":false,"number":0,"disabled":true},{"name":"Exclusive","id":"EX","selected":false,"number":0,"disabled":true},{"name":"Electric","id":"ELC","selected":false,"number":0,"disabled":true},{"name":"Paddy Hopkirk Edition","id":"P4","selected":false,"number":0,"disabled":true},{"name":"John Cooper Works","id":"JCW","selected":false,"number":0,"disabled":true}],"performance":[{"name":"One","id":"perf_one","selected":false,"number":0,"disabled":true},{"name":"Cooper","id":"perf_cooper","selected":false,"number":0,"disabled":true},{"name":"Cooper ALL4","id":"perf_coop_4","selected":false,"number":0,"disabled":true},{"name":"Cooper D","id":"perf_coope_d","selected":false,"number":0,"disabled":true},{"name":"Cooper D ALL4","id":"perf_coop_d_4","selected":false,"number":0,"disabled":true},{"name":"Cooper S","id":"perf_coope_s","selected":false,"number":0,"disabled":true},{"name":"Cooper S ALL4","id":"perf_coop_s_4","selected":false,"number":0,"disabled":true},{"name":"Cooper S E ALL4 PHEV","id":"perf_hybrid","selected":false,"number":0,"disabled":true},{"name":"JOHN COOPER WORKS","id":"perf_jcw","selected":false,"number":0,"disabled":true}]}}'

            carMake = 'Mini'
            item = CarItem()
            item['CarMake'] = carMake
            item['CarModel'] = self.remove_special_char_on_excel(carModel)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = float(MonthlyPayment)
            item['CustomerDeposit'] = float(CustomerDeposit)
            item['RetailerDepositContribution'] = DepositContribution
            item['OnTheRoadPrice'] = float(OnTheRoadPrice)
            item['DurationofAgreement'] = Term
            item['OptionToPurchase_PurchaseActivationFee'] = '0.00'
            item['RepresentativeAPR'] = RepresentativeAPR
            item['AverageMilesPerYear'] = AnnualMileage
            item['OfferExpiryDate'] = OfferExpiryDate
            item['RetailCashPrice'] = OnTheRoadPrice
            item['CarimageURL'] = car_image
            item['DebugMode'] = self.Debug_Mode
            item['WebpageURL'] = WebpageURL

            data_url = "https://services.codeweavers.net/api/BMW/QuoteData?QuoteReference="+QuoteReference+"&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW&Referrer="

            # print("data_jitemson", item)
            # print("response_link", response_link)
            # print("respo", response.url)
            # input("stop")

            yield Request(data_url, callback=self.parse_car_items, headers=self.headers, meta={"items":item, "QuoteReference":QuoteReference})


    # def parse_car_json_url(self, response):
    #     """ pasrse url for geting Final payment(json)
    #     """
    #     ### Taking FinalPayment /pass QuoteReference###
    #     QuoteReference = response.meta['QuoteReference']
    #     data_url = "https://services.codeweavers.net/api/BMW/QuoteData?QuoteReference="+QuoteReference+"&apiKey=OuX25F2Ud76Y1eByms&systemKey=BMW&Referrer="
    #     # data_url = "https://services.codeweavers.net/api/BMW/RetrieveQuote?ApiKey=OuX25F2Ud76Y1eByms&QuoteReference="+QuoteReference+"&Referrer=https:%2F%2Foffers.mini.co.uk%2F&SystemKey=BMW"
    #     # data_url = "https://services.codeweavers.net/api/BMW/RetrieveQuote?ApiKey=OuX25F2Ud76Y1eByms&QuoteReference="+QuoteReference+"&Referrer=https:%2F%2Foffers.mini.co.uk%2Foffers%2F252973a6-80f1-40a1-8e12-a59fe8d472b6&SystemKey=BMW"
    #     WebpageURL = response.url
    #     item = response.meta['items']
    #     yield Request(data_url, callback=self.parse_car_items, headers=self.headers, meta={"items":item, "WebpageURL":WebpageURL})


    def parse_car_items(self, response):
        """ pasrse url for geting Final payment(json)
        """
    
        item = response.meta['items']
        data_json = json.loads(response.body)
        # print("data_json", data_json)
        # print("respo", response.url)
        # input("stop")
        offers = data_json['Quote']

        OptionalPurchase_FinalPayment = offers['FinalPayment']
        if "Hire Purchase" in item['TypeofFinance']:
            OptionalPurchase_FinalPayment = 'N/A'
        ExcessMilageCharge = offers['ExcessMileageRate']
        FixedInterestRate_RateofinterestPA = offers['RateOfInterest']
        TotalAmountPayable = offers['TotalAmountPayable']
 

        item = response.meta['items']
        if "AmountOfCredit" in offers:
            item['AmountofCredit'] = offers['Balance']
        else:
            item['AmountofCredit'] = 'N/A'    
        item['OptionalPurchase_FinalPayment'] = OptionalPurchase_FinalPayment
        item['ExcessMilageCharge'] = self.remove_percentage_sign(str(ExcessMilageCharge))
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(str(FixedInterestRate_RateofinterestPA))
        item['TotalAmountPayable'] = TotalAmountPayable

        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        yield item
