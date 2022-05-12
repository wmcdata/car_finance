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
import ast
import json
from time import gmtime, strftime

# https://tools.seat.co.uk/finance-calculator/#/ ############# <-   Start from this url
# https://www.seat.co.uk/offers/new-cars/new-car-offers.html
class SeatSpider(BaseSpider):
    name = "seat.co.uk"
    allowed_domains = ['seat.co.uk']
    start_url = ['https://tools.seat.co.uk/finance-calculator/','http://www.seat.co.uk/offers/contract-hire/overview.html']
    base_url  = 'https://tools.seat.co.uk/finance-calculator/#/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        # 'Proxy-Authorization': basic_auth_header('watchmycompetitor', 'dmt276gnw845')
    }

    def __init__(self):
        super(SeatSpider, self).__init__()
    def start_requests(self):
        for url in self.start_url:
            if "contract-hire" in url:
                yield Request(url, callback=self.parse_model_url_hire_contract, headers=self.headers)
            else:
                yield Request(url, callback=self.main_page, headers=self.headers)

    def parse_model_url_hire_contract(self, response):

        url_path = response.xpath('//div[@id="navbarContent"]/ul/li')
        for href in url_path:
            url = self.getText(href, './/a/@href')
            href = response.urljoin(url)
            # print("href:" , href)
            # print("url:" , response.url)
            # input("stop")
            if "overview.html" not in href and "/driverline.html" not in href:
                yield Request(href, dont_filter=True, callback=self.parse_model, headers=self.headers)
                
    ###############################******############################## 
    def check_label_status(self,label,available_brands):
        for brand in available_brands:
            if brand in label:
                return True
        return False
    def return_brand_name(self,label,available_brands):
        for brand in available_brands:
            if brand in label:
                return brand
        return False
    ##############################******###############################
         
    def main_page(self,response):
        #yield{'URL':response.url}
        main_content = response.xpath('//script[contains(text(),"window.jahiaConfig")]')[0].xpath('.//text()')[0].get().replace('window.jahiaConfig = ','').strip().strip(';')
        main_content = json.loads(main_content)
        available_brands = [item.get('label') for item in main_content.get('data').get('pages').get('calculator').get('models')]
        available_brands.remove('Leon')
        available_brands.append('Leon')
        
        url_format = 'https://www.seat.co.uk/offers/new-cars/{}/solutions-pcp-offer.html'
        leon_format = 'https://www.seat.co.uk/offers/new-cars/leon-family/{}.html'
        respective_link = {brand_name:leon_format.format(brand_name.lower().replace(' ','-')) if 'Leon' in brand_name else url_format.format(brand_name.lower().replace(' ','-')) for brand_name in available_brands}
        #input('waiting')
        engines = main_content.get('data').get('pages').get('calculator').get('engines')
        available_engines = list()
        for engine in engines:
            label = engine.get('label')
            if self.check_label_status(label,available_brands):
                available_engines.append(engine)
        for engine in available_engines:
            cap_code = engine.get('capCode')
            price = engine.get('price')
            id_url = f'https://tools.seat.co.uk/api/finance/2.0/capCode/{cap_code}/products?price={price}&brandCode=SEAT'
            car_model = engine.get('label')
            brand = self.return_brand_name(car_model,available_brands)
            BRANDURL  = respective_link.get(brand)
            yield Request (id_url,callback=self.solution_request,meta={'capcode':cap_code,'price':price,'car_model':car_model,'BRANDURL':BRANDURL},headers=self.headers)
           
    def solution_request(self,response):
        # months_list =[18,24,30,36,42,48]
        # months = months_list[0]
        # annual_mileage_list = [5,10,15,20,25,30]
        # annual_mileage = annual_mileage_list[-1]
        # userDeposit = 3500
        response_body = json.loads(response.body.decode('utf8'))
        # print("response_body:", response_body)
        # print("resp_url: ", response.url)
        if "retailProducts" in response_body:
            retail_products = response_body.get('retailProducts')
        
           
            if len(retail_products) > 0:
                retail_products= retail_products[0]
                prod_id = retail_products.get('productId')
                credit = retail_products.get('productType')
                price = response.meta['price']
                capcode = response.meta['capcode']
                model = response.meta.get('car_model')
                #parameterized_URL =  f'https://tools.seat.co.uk/api/finance/2.0/capCode/{capcode}/personal/{credit}/calculations?periodOfMonths={months}&annualMileage={annual_mileage}&deposit={userDeposit}&price={price}&productId={prod_id}&brandCode=SEAT'
                final_URL = f'https://tools.seat.co.uk/api/finance/2.0/capCode/{capcode}/personal/{credit}/calculations?price={price}&productId={prod_id}&brandCode=SEAT'
                yield Request(final_URL,callback=self.get_fiances_information,meta={'car_model':model,'URL':response.meta['BRANDURL']})
               
                      
        #input('')
    def get_fiances_information(self,response):
        response_body = json.loads(response.body)
        calculations = response_body.get('calculations')[0]
        na = 'N/A'
        disclaimer = calculations.get('disclaimer').replace('(','').replace(')','')
        if 'PCP'  in disclaimer:
            type_of_fianance = 'PCP'
        else:
            type_of_fianance = 'PCH'
        expiry = disclaimer.split('ordered by ')[-1].split('from')[0].strip()
        parameters = calculations.get('parameters',na)
        on_road_price = calculations.get('retailPrice',na)
        deposit = parameters.get('deposit',na)
        period_of_months = parameters.get('periodOfMonths',na)
        annual_mill = parameters.get('annualMileage',na)
        
        excess_mill = parameters.get('excessMileage',na)
        total_amount_credit = parameters.get('amountFinanced',na)
        details = calculations.get('details',[])
        for detail in details:
            if detail.get('id') == 'DEPCONT':
                retailer_deposit= detail.get('value')
            if detail.get('id') == 'GFV':
                optional_final_pay = detail.get('value')
            if detail.get('id') == 'OTPFEE':
                opt_purchase_fee = detail.get('value')
            if detail.get('id') == 'TAP':
                total_pay_amount = detail.get('value')
            if detail.get('id') == 'APR':
                apr = detail.get('value')
            if detail.get('id') == 'AER':
                Rate_of_interest = detail.get('value')
            if detail.get('id') == 'Rate':
                monthly_payment = detail.get('value')
                
        item = CarItem()
        item['CarMake'] = 'Seat'
        item['CarModel'] = response.meta['car_model']
        item['TypeofFinance'] = self.get_type_of_finance(type_of_fianance)
        item['MonthlyPayment'] = monthly_payment
        item['CustomerDeposit'] = deposit
        item['RetailerDepositContribution'] = retailer_deposit
        item['OnTheRoadPrice'] = on_road_price
        item['AmountofCredit'] = total_amount_credit
        item['DurationofAgreement'] = period_of_months
        item['OptionalPurchase_FinalPayment'] = optional_final_pay
        item['TotalAmountPayable'] = total_pay_amount
        item['OptionToPurchase_PurchaseActivationFee'] = opt_purchase_fee
        item['RepresentativeAPR'] = apr
        item['FixedInterestRate_RateofinterestPA'] = Rate_of_interest
        item['ExcessMilageCharge'] = excess_mill
        if "10" in str(annual_mill):
            item['AverageMilesPerYear'] = '10000'
        elif "9" in str(annual_mill):
            item['AverageMilesPerYear'] = '9000' 
        elif "8" in str(annual_mill):
            item['AverageMilesPerYear'] = '8000'        
        else:
            item['AverageMilesPerYear'] = 'N/A'

        item['OfferExpiryDate'] = expiry
        item['RetailCashPrice'] = on_road_price
        item['WebpageURL'] = response.meta['URL']
        item['DebugMode'] = self.Debug_Mode
        item['CarimageURL'] = na
        try:
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['FinalPaymentPercent'] = "N/A"
            item['DepositPercent'] = "N/A"
        yield item


    def parse_model(self, response):
        """CONTRACT HIRE OFFERS
        """
        ### contract-hire ####
        # offer_expiry = str()
        # offer_text = self.getTextAll(response, '//div[@id="disclaimer"]//p[contains(text(), "Ordered by")]//text()')
        # if not offer_text:
        #     offer_text = response.xpath('//div[@id="disclaimer"]//p//text()').extract()[3]
        # elif not offer_text:
        #     offer_expiry = offer_text.split("Ordered by")[1].split("from participating")[0]
        # else:
        #     offer_expiry = 'N/A'

        # offer_text = self.getTextAll(response, '//div[@id="disclaimer"]//p[contains(text(), "Ordered by")]//text()')
        # if not offer_text:
        #     offer_text = self.getTextAll(response, '//div[@id="disclaimer"]//p/b/following-sibling::text()')

        # offerExp = offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        # OfferExpiryDate = self.dateMatcher(offerExp)[0]
        OfferExpiryDate = '30/06/2022'
        carImg = self.getText(response, '//div[@class="cont-img"]/span/div/span/@data-src')

        data_path = response.xpath('//div[@class="container-body"]//div[@class="cont-module"]')
        for data in data_path:
            model1 = self.getText(data, './/h6[@class="title"]/text()')
            subtitle = self.getText(data, './/div[@class="subtitle"]/text()')
            if not subtitle:
                subtitle = response.xpath('//div[@class="subtitle"]/text()').extract()[0].split("-")[1].strip()
            model2 = subtitle.split("-")[0]
            carModel = model1 +" "+ model2
            if " - " in subtitle:
                OTR = subtitle.split(" - ")[1]
            else:
               OTR = subtitle



            # print("OTR:" , OTR)
            # # print("OTR:" , OTR)
            # print("url:" , response.url)
            # input("stop")
            if "OTR" in OTR:
                OnTheRoadPrice = OTR.split("OTR")[0]
            else:
                OnTheRoadPrice = 'N/A'

            # if "contract-hire/tarraco.html" in response.url:
            #     print("OTR:" , OTR)
            #     print("subtitle:" , subtitle)
            #     print("OnTheRoadPrice:" , OnTheRoadPrice)
            #     print("url:" , response.url)
            #     input("stop")
            customer_deposit = self.getText(data, './/div[@class="container-tags-icon"]/span/text()')
            if not customer_deposit:
                customer_deposit = response.xpath('//div[@class="container-tags-icon"]/span/text()').extract()[3]

            CustomerDeposit = customer_deposit.split("Initial rental")[1]
            milleage = self.getText(data, './/div[@class="container-tags-icon"]/span[2]/text()')
            if not milleage:
                milleage = response.xpath('//div[@class="container-tags-icon"]/span/text()').extract()[5]
            ExcessMilageCharge = milleage.split("Excess mileage")[1].split("p")[0]
            MonthlyPayment = self.getText(data, './/div[@class="price"]/span[@class="text-bold"]/text()')

            # print("title:" , MonthlyPayment)
            # print("subtitle:" , carModel)
            # print("customer_deposit:" , CustomerDeposit)
            # print("OTR:" , OTR)
            # print("offer_expiry:" , offer_text)
            # print("url:" , response.url)
            # input("stop")

            item = CarItem()
            item['CarMake'] = 'Seat'
            item['CarModel'] = self.remove_special_char_on_excel(carModel)
            item['TypeofFinance'] = self.get_type_of_finance('Business Contract Hire')
            item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
            item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
            if item['MonthlyPayment']:
                item['MonthlyPayment'] = float(item['MonthlyPayment'])
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
            if item['CustomerDeposit']:
                item['CustomerDeposit'] = float(item['CustomerDeposit'])
            item['ExcessMilageCharge'] = ExcessMilageCharge
            item['RetailerDepositContribution'] = "N/A"
            item['OptionalPurchase_FinalPayment'] = "N/A"
            item['AmountofCredit'] = "N/A"
            item['DurationofAgreement'] = "36"
            item['TotalAmountPayable'] = "N/A"
            item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
            item['RepresentativeAPR'] = "N/A"
            # item['OfferExpiryDate'] = '31/03/2021'
            item['OfferExpiryDate'] = OfferExpiryDate
            item['FixedInterestRate_RateofinterestPA'] = "N/A"
            item['DebugMode'] = self.Debug_Mode
            try:
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['FinalPaymentPercent'] = ""
                item['DepositPercent'] = ""
            item['AverageMilesPerYear'] = '10000'
            item['CarimageURL'] = response.urljoin(carImg)
            item['WebpageURL'] = response.url
            if item['MonthlyPayment'] !='':
                yield item
