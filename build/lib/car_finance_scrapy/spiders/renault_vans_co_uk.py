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

class RenaultSpider(BaseSpider):
    name = "renault-vans.co.uk"

    allowed_domains = ['renault.co.uk']

    start_url = 'https://offers.renault.co.uk/business'
    def __init__(self):
        super(RenaultSpider, self).__init__()

    def start_requests(self):
        yield Request(self.start_url, callback=self.parse_model_url, headers=self.headers)

    def parse_model_url(self, response):
        """VANS OFFERS CH
        """
        vansloop = response.xpath('//div[@class="grid-container"]/div[@class="grid-item"]')
        for href in vansloop:
            model = self.getText(href, './/h3/text()')
            url = self.getText(href, './/a[contains(text(), "View offers")]/@href')

            CarimageURL = self.getText(href, './/div/img/@src')
            urls = response.urljoin(url)
            # print(urls)
            # input()
            if "kangooze_business" in urls or "master_business" in urls or "trafic_business" in urls or "kangoovan_business" in urls or "hirepurchase" in urls or "Trafic-Passenger-business" in urls or "new-master-ze" in urls or "conversions" in urls:
                Premodel = model
                # if "hirepurchase" in urls:
                #     TypeofFinance = "Hire Purchase"
                #     AverageMilesPerYear = 10000
                #     linkVan = urls
                # else:
                
                
                # WebpageURL = "https://offers.renault.co.uk/business/megane_business/contract-hire-36?offer="+str(model['Id'])
                # linkVan =  urls.replace("hirepurchase", "contract-hire-48")
                # print(urls)
                # input()
                yield Request(urls, callback=self.parse_model_link, headers=self.headers, dont_filter=True, meta={"Premodel":Premodel, "CarimageURL":CarimageURL})

    def parse_model_link(self, response):
        """
        """
        # print(response.url)
        # input()
        CarimageURL =  response.meta['CarimageURL']
        Premodel =  response.meta['Premodel']
        financeLinks  = response.url

        if "kangooze_business" in financeLinks:
            linkVan =  financeLinks.replace("hirepurchase", "contract-hire-36")
        elif "trafic_business" in financeLinks:
            linkVan =  financeLinks.replace("hirepurchase", "contract-hire-24") 
        elif "master_business" in financeLinks:
            linkVan =  financeLinks.replace("hirepurchase", "contract-hire-24")
        elif "conversions" in financeLinks:
            linkVan =  financeLinks.replace("hirepurchase", "contract-hire-24")                          
        elif "contract-hire-" not in financeLinks:
            linkVan =  financeLinks.replace("hirepurchase", "contract-hire-48")
        elif "contract-hire-" not in financeLinks:
            linkVan =  financeLinks.replace("hirepurchase", "contract-hire-24")    
        else:
            linkVan =  financeLinks.replace("hirepurchase", "contract-hire-24")    

        print("response.url", linkVan)
        # print(response.url)
        # input()

        yield Request(linkVan, callback=self.parse_model_data, headers=self.headers, dont_filter=True, meta={"Premodel":Premodel, "CarimageURL":CarimageURL}) 
        # else: ### Hire purchase not working
        #     yield Request(financeLinks, callback=self.parse_model_data, headers=self.headers, meta={"Premodel":Premodel, "CarimageURL":CarimageURL}) 


    def _find_dict(self, dic, kw, finv=True):
        for k in dic:
            if kw.lower() in k.lower():
                return dic[k]
        if finv:
            for k in dic:
                if kw.lower() in dic[k].lower():
                    return dic[k]

        return ''

    def parse_model_data(self, response):
        """vans offers
        """
        # print("RESPONSEURL: ", response.url)
        # input('wait')
        CarimageURL =  response.meta['CarimageURL']
        PreModel =  response.meta['Premodel']
        AverageMilesPerYear = 10000
        TypeofFinance = "Commercial Contract Hire"
        PostModel =  self.getTexts(response, '//p[@class="card_name"]/text()')
       
        Duration =  self.getText(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "35 Monthly Rentals of") or contains(text(), "23 Monthly Rentals of") or contains(text(), "47 Monthly Rentals of")]/text()')
        if "35" in Duration:
            DurationofAgreement = '36'
        elif "47" in Duration:
            DurationofAgreement = '48'
        elif "23" in Duration:
            DurationofAgreement = '24'    

        MonthlyPayment = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "35 Monthly Rentals of") or contains(text(), "23 Monthly Rentals of") or contains(text(), "47 Monthly Rentals of")]/following-sibling::td/text()')
        CustomerDeposit = self.getTexts(response, './/table[@class="striped"]//tbody/tr//td[contains(text(), "Advance Payment")]/following-sibling::td/text()')
       
        i = 0
        for x in MonthlyPayment:
            MonthlyPayments = x


            item = CarItem()
            item['CarMake'] = 'Renault'
            try:
                if PostModel != []:
                    item['CarModel'] = self.remove_special_char_on_excel(PreModel +' '+ PostModel[i])
                else:
                    item['CarModel'] = self.remove_special_char_on_excel(PreModel)
            except:
                item['CarModel'] = self.remove_special_char_on_excel(PreModel)
            item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayments)
            if item['MonthlyPayment']:
                item['MonthlyPayment'] = float(item['MonthlyPayment'])
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit[i])
            if item['CustomerDeposit']:
                item['CustomerDeposit'] = float(item['CustomerDeposit'])
            item['RetailerDepositContribution'] = 'N/A'

            item['OnTheRoadPrice'] = 'N/A'
            item['OptionalPurchase_FinalPayment'] = 'N/A'

            item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = DurationofAgreement
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
      
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = "N/A"
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] = AverageMilesPerYear
            item['RetailCashPrice'] = 'N/A'
            item['OfferExpiryDate'] = "30/06/2022"
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent']  = float()
            item['CarimageURL'] = CarimageURL
            item['WebpageURL'] = response.url
            if item['MonthlyPayment'] != '':
                i += 1
                yield item


        # jO = json.loads(response.body)

        # name = jO['result']['Name']
        # for model in jO['result']['Cars']:
        #     offer_text = model['TermsConditions']
        #     offerExp = offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        #     OfferExpiryDate = self.dateMatcher(offerExp)[0]

        #     # if "registered before " in offer_text:
        #     #     OfferExpiryDate = offer_text.split(" registered before ")[1].split(".")[0]
        #     # elif "registered by " in offer_text:
        #     #     OfferExpiryDate = offer_text.split("registered by ")[1].split(".")[0]
        #     # else:
        #     #     OfferExpiryDate =  offer_text

        #     if "hirepurchase" in model['LinkQuote']:
        #         TypeofFinance = "Hire Purchase"
        #         AverageMilesPerYear = int()
        #         WebpageURL = "https://offers.renault.co.uk/business/master_business/hirepurchase?offer="+str(model['Id'])
        #     else:
        #         TypeofFinance = "Commercial Contract Hire"

        #         AverageMilesPerYear = 10000
        #         WebpageURL = "https://offers.renault.co.uk/business/megane_business/contract-hire-36?offer="+str(model['Id'])

        #     dic = dict(zip(model['RepresentativeExample']['Cols'][0],model['RepresentativeExample']['Cols'][-1]))
        #     Duration = model['RepresentativeExample']['TableHead'][0]['Duration']

        #     CarModel = name + ' ' + model['Version']
        #     if "Business" in CarModel:
        #         CarModel = CarModel.split("Business")[0]

        #     item = CarItem()
        #     item['CarMake'] = 'Renault'
        #     item['CarModel'] = self.remove_special_char_on_excel(CarModel)
        #     item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
        #     item['MonthlyPayment'] = self.remove_gbp(self._find_dict(dic, 'Monthly payments'))
        #     if item['MonthlyPayment']:
        #         item['MonthlyPayment'] = float(item['MonthlyPayment'])
        #     item['CustomerDeposit'] = self.remove_gbp(self._find_dict(dic, 'Customer deposit'))
        #     if item['CustomerDeposit']:
        #         item['CustomerDeposit'] = float(item['CustomerDeposit'])
        #     if not (item['MonthlyPayment']):
        #         item['MonthlyPayment'] = self.remove_gbp(self._find_dict(dic, 'Monthly Rentals'))
        #     if not (item['CustomerDeposit']):
        #         item['CustomerDeposit'] = self.remove_gbp(self._find_dict(dic, 'Advance Payment'))
        #     item['RetailerDepositContribution'] = self.remove_gbp(self._find_dict(dic, 'Dealer deposit contribution'))
        #     if item['RetailerDepositContribution']:
        #         item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
        #     item['OnTheRoadPrice'] = self.remove_gbp(self._find_dict(dic, 'Cash price'))
        #     if item['OnTheRoadPrice']:
        #         item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
        #     item['OptionalPurchase_FinalPayment'] = self.remove_gbp(self._find_dict(dic, 'Optional final payment'))
        #     item['AmountofCredit'] = self.remove_gbp(self._find_dict(dic, 'Total amount of credit'))
        #     item['DurationofAgreement'] = Duration
        #     item['TotalAmountPayable'] = self.remove_gbp(self._find_dict(dic, 'Total amount payable'))
        #     item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(self._find_dict(dic, 'Option to purchase fee'))
        #     item['RepresentativeAPR'] = self._find_dict(dic, 'APR')
        #     item['FixedInterestRate_RateofinterestPA'] = self._find_dict(dic, 'Fixed interest rate p.a.')
        #     txt= model['TermsConditions']
        #     item['ExcessMilageCharge'] = self.reText(txt, r'excess mileage(.*?) per mile').strip()
        #     item['AverageMilesPerYear'] = AverageMilesPerYear
        #     item['OfferExpiryDate'] = OfferExpiryDate
        #     item['OfferExpiryDate'] = '30/09/2021'
        #     item['DebugMode'] = self.Debug_Mode
        #     item['RetailCashPrice'] = self.remove_gbp(self._find_dict(dic, 'Cash price'))
        #     item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        #     try:
        #         item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        #     except:
        #         item['DepositPercent'] = float()
        #     src = model['ModelInfo']['Image']
        #     if src != '' and src != None:
        #         item['CarimageURL'] = response.urljoin(src)

        #     item['WebpageURL'] = WebpageURL
        #     # item['WebpageURL'] = response.urljoin(model['ModelInfo']['Discover'])
        #     if item['MonthlyPayment'] != '':
        #         yield item
