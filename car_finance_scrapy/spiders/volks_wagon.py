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
import time

# 'https://www.volkswagen.co.uk/offers-and-finance/finance-calculator'
class VolksWagonsSpider(BaseSpider):
    name = "volks.wagon"
    allowed_domains = []
    holder = list()
    start_url = ['https://www.volkswagen.co.uk/api/finance/3.3/derivatives', 'https://www.volkswagen.co.uk/car-finance/new-car-deals']
    base_url = 'https://www.volkswagen.co.uk/'

    def __init__(self):
        super(VolksWagonsSpider, self).__init__()
        self.i = 0

    def start_requests(self):
        for url in self.start_url:
            if "/finance/3.3/derivatives" in url:
                yield Request(url, callback=self.parse_2_derivatives, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_3_derivatives, headers=self.headers)


    def parse_2_derivatives(self, response):
        """ Start request
        """
        # session = Session()
        # session.head('https://www.volkswagen.co.uk/finance-calculator')
        #
        # response_pch = session.post(
        # url='https://www.volkswagen.co.uk/api/finance/2.0/derivatives',
        # headers={
        # 'Referer': 'https://www.volkswagen.co.uk/finance-calculator',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        # 'Accept': 'application/json, text/javascript, */*; q=0.01',
        # 'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate',
        # 'Content-Type':'application/json; charset=UTF-8',
        # 'X-Requested-With':'XMLHttpRequest'
        # }
        # )

        cars_pch = json.loads(response.body)
        # print("cars_pch: ", cars_pch)
        # input("stop")
        for cars in cars_pch['models']:
            model = cars['title']
            model_id = cars['id']
            trims = cars['trims']
            for derivatives in trims:
                variations = derivatives['derivatives']
                trim_id = derivatives['id']
                for var in variations:
                    derivative_id = str(var['id'])
                    variation_model = model+' '+var['title']
                    ajax_urls = ['https://www.volkswagen.co.uk/api/finance/3.3/calculations/derivatives/'+derivative_id+'/personal/SOLUTIONS?annualMileage=10&periodOfMonths=36&deposit=2500.0', 'https://www.volkswagen.co.uk/api/finance/3.3/calculations/derivatives/'+derivative_id+'/business/CONTRACT_HIRE?servicePlan=NOPLAN&rentalsInAdvance=3&annualMileage=10&periodOfMonths=48']

                    # ajax_urls = ['https://www.volkswagen.co.uk/api/finance/3.1/quote/'+derivative_id+'/personal?annualMileage=10&periodOfMonths=48&deposit=2000.00','https://www.volkswagen.co.uk/api/finance/3.1/quote/'+derivative_id+'/business?annualMileage=10&periodOfMonths=48&deposit=2000.00']
                    # url = 'http://www.volkswagen.co.uk/new/range'

                    for ajax_url in ajax_urls:
                        # print("ajax_urls: ", ajax_url)
                        # input("stop")
                        time.sleep(0.5)
                        yield Request(ajax_url, callback=self.parse_item, headers=self.headers_ajax, meta={'model': variation_model, 'model_id':model_id,'trim_id':trim_id, 'derivative_id':derivative_id, 'ajax_url':ajax_url})

    def parse_3_derivatives(self, response):
        """ Start request
        """

        anchor_path = response.xpath('//a[@class="car-model-card"]')
        for a in anchor_path:
            url = self.getText(a, './@href')
            href = urljoin(response.url, url)
            # print("href: ", href)
            # input("stop")
            yield Request(href, callback=self.parse_next_link, headers=self.headers)

    def parse_next_link(self, response):
        """ Start parse_next_link
        """
        model_and_finance= self.getTexts(response, "//h4/text()")
        for typo in model_and_finance:
            # print("response: ", response.url)
            # print("typo: ", typo)
            # input("stop")
            if "Personal Contract Plan" in typo:
                if "per annum for a" in typo:
                    car_model = typo.split("per annum for a")[1]
                elif "per annum for" in typo:
                    car_model = typo.split("per annum for")[1]

                Duration = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Duration")]]]/following-sibling::td//span/text()')
                term = [x.strip() for x in Duration if x.strip()]

                payment = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "monthly payments of")]]]/following-sibling::td//span/text()')
                monthly_payment = [x.strip() for x in payment if x.strip()]

                # dep_contr = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Deposit contribution")]]]/following-sibling::td//span/text()')
                # depositContribution = [x.strip() for x in dep_contr if x.strip()]

                otr = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Retail cash price")]]]/following-sibling::td//span/text()')
                OnTheRoadPrice = [x.strip() for x in otr if x.strip()]

                deposit = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Customer deposit") or contains(text(), "Deposit")]]]/following-sibling::td//span/text()')
                customer_deposit = [x.strip() for x in deposit if x.strip()]

                fee = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Option to purchase fee")]]]/following-sibling::td//span/text()')
                OptionToPurchase_PurchaseActivationFeefee  = [x.strip() for x in fee if x.strip()]

                opt_final_pay = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Optional final payment")]]]/following-sibling::td//span/text()')
                OptionalPurchase_FinalPayment = [x.strip() for x in opt_final_pay if x.strip()]

                amount_payable = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Total amount payable")]]]/following-sibling::td//span/text()')
                totalAmountPayable = [x.strip() for x in amount_payable if x.strip()]

                amount_credit = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Total amount of credit")]]]/following-sibling::td//span/text()')
                AmountofCredit = [x.strip() for x in amount_credit if x.strip()]

                representative_apr = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Representative APR")]]]/following-sibling::td//span/text()')
                APR = [x.strip() for x in representative_apr if x.strip()]

                rate_interest = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Rate of interest p.a.")]]]/following-sibling::td//span/text()')
                FixedInterestRate_RateofinterestPA = [x.strip() for x in rate_interest if x.strip()]

                # deposit_contr = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Deposit contribution ")]]]/following-sibling::td//span/text()')
                # RetailerDepositContribution = [x.strip() for x in deposit_contr if x.strip()]


                excessMileage = self.getTexts(response, '//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Excess mileage charge")]]]/following-sibling::td//span/text()')
                ExcessMilageCharge = [x.strip() for x in excessMileage if x.strip()]

                Offer_text = self.getTextAll(response, '//div[@class="accordion__content"]/p/text()')
                offerExp = Offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
                OfferExpiryDate = self.dateMatcher(offerExp)[0]


                i = 0
                for x in monthly_payment:
                    monthly_payment = x

                    # print("term: ", term[i])
                    # print("month_pay: ", monthly_payment)
                    # print("depositContribution: ", depositContribution[i])
                    # print("OnTheRoadPrice: ", OnTheRoadPrice[i])
                    # print("customer_deposit: ", customer_deposit[i])
                    # print("OptionToPurchase_PurchaseActivationFeefee: ", OptionToPurchase_PurchaseActivationFeefee[i])
                    # print("OptionalPurchase_FinalPayment: ", OptionalPurchase_FinalPayment[i])
                    # print("AmountofCredit: ", AmountofCredit[i])
                    # print("APR: ", APR[i])
                    # print("FixedInterestRate_RateofinterestPA: ", FixedInterestRate_RateofinterestPA[i])
                    # print("ExcessMilageCharge: ", ExcessMilageCharge[i])
                    # input("stop")
                    duration_of_agreement = term[i].split(" years")[0].strip()
                    if "4" in duration_of_agreement:
                        DurationofAgreement = '48'
                    else:
                        DurationofAgreement = '36'

                    # if "https://www.volkswagen.co.uk/car-finance/new-car-deals/up" in response.url:
                    #     print("url", response.url)
                    #     print("cust", customer_deposit[i])
                    #     input("stop")
                    car_make = "Volkswagen"
                    item = CarItem()
                    item['CarMake'] = car_make
                    item['CarModel'] = self.remove_special_char_on_excel(car_model)
                    item['TypeofFinance'] = self.get_type_of_finance('Personal Contract Plan')
                    item['MonthlyPayment'] =  self.make_two_digit_no(monthly_payment)
                    if item['MonthlyPayment']:
                        item['MonthlyPayment'] = float(item['MonthlyPayment'])
                    item['CustomerDeposit'] =  self.make_two_digit_no(customer_deposit[i])
                    item['RetailerDepositContribution'] = ''
                    item['OnTheRoadPrice'] =  self.remove_gbp(OnTheRoadPrice[i])
                    item['AmountofCredit'] =  self.remove_gbp(AmountofCredit[i])
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                    item['OptionalPurchase_FinalPayment'] =  self.remove_gbp(OptionalPurchase_FinalPayment[i])
                    item['TotalAmountPayable'] = self.remove_gbp(totalAmountPayable[i])
                    item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(OptionToPurchase_PurchaseActivationFeefee[i])
                    item['RepresentativeAPR'] = self.remove_percentage_sign(APR[i])
                    item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA[i])
                    if len(ExcessMilageCharge) > 0:
                        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge[i])
                    else:
                        item['ExcessMilageCharge'] = 'N/A'

                    item['AverageMilesPerYear'] = '10000'
                    item['RetailCashPrice'] =  self.remove_gbp(OnTheRoadPrice[i])
                    # item['OfferExpiryDate'] = '31/03/2021'
                    item['OfferExpiryDate'] = OfferExpiryDate
                    item['WebpageURL'] = response.url
                    item['CarimageURL'] = ''
                    item['DebugMode'] = self.Debug_Mode
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    try:
                        item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                    except:
                        item['DepositPercent'] = float()
                    if item['MonthlyPayment'] != '':
                        i += 1
                        yield item
            elif "Contract Hire" in typo:
                if "3 years" in typo:
                    Duration = '36'
                else:
                    Duration = '24'


                Offer_text = self.getTextAll(response, '//div[@class="accordion__content"]/p/text()')
                offerExp = Offer_text.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
                OfferExpiryDate = self.dateMatcher(offerExp)[0]


                # Offer_text = self.getText(response, '//div[@class="accordion__content"]/p[contains(text(), "Valid until")]/text()')
                # OfferExpiryDate = Offer_text.split("Valid until ")[1].split(".")[0]
                # print("response: ", response.url)
                # print("Offer_text: ", OfferExpiryDate)
                # input("stop")

                car_model = typo.split(",")[0]

                Cus_deposit =  response.xpath('//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Initial rental")]]]/following-sibling::td//span/text()').extract()
                CustomerDeposit = [x.strip() for x in Cus_deposit if x.strip()]

                month_pay =  response.xpath('//div[@class="richtext-table richtext-table--offers-table"]/table/tbody/tr/th[span[span[contains(text(), "Monthly rental")]]]/following-sibling::td//span/text()').extract()
                MonthlyPayment = [x.strip() for x in month_pay if x.strip()]

                # print("url", response.url)
                # print("CustomerDeposit", CustomerDeposit)
                # print("monthly_payment", MonthlyPayment)
                # input("stop")

                car_make = "Volkswagen"
                item = CarItem()
                item['CarMake'] = car_make
                item['CarModel'] = self.remove_special_char_on_excel(car_model)
                item['TypeofFinance'] = self.get_type_of_finance('Business Contract Hire')
                item['MonthlyPayment'] =  self.make_two_digit_no(MonthlyPayment[0])
                item['CustomerDeposit'] =  self.make_two_digit_no(CustomerDeposit[0])
                item['RetailerDepositContribution'] = 'N/A'
                item['OnTheRoadPrice'] = ''
                item['AmountofCredit'] = ''
                item['DurationofAgreement']   = Duration
                item['OptionalPurchase_FinalPayment'] = ''
                item['TotalAmountPayable'] = ''
                item['OptionToPurchase_PurchaseActivationFee'] = ''
                item['RepresentativeAPR'] = ''
                item['FixedInterestRate_RateofinterestPA'] = ''
                item['ExcessMilageCharge'] = '6'
                item['AverageMilesPerYear'] = '10000'
                item['RetailCashPrice'] = ''
                item['OfferExpiryDate'] = OfferExpiryDate
                item['WebpageURL'] = response.url
                item['CarimageURL'] = ''
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                if item['MonthlyPayment'] != '':
                    yield item

    def get_image(self, response):
        # print("url : ", response.xpath('//div[@class="container"]//div[@class="col-md-5"]/img/@src').extract())
        # input("wait in get_image")
        item = response.meta['item']
        model_id = response.meta['model_id']

        CarImageUrl = response.xpath('//ul/li[@class="col-6"]/a[@data-model-id='+str(model_id)+']/img/@src').extract()
        yield item


    def parse_item(self, response):
        """ Function for parse category
        """
        car_make = "Volkswagen"
        car_model = response.meta['model']
        model_id = response.meta['model_id']
        trim_id = response.meta['trim_id']
        derivative_id = response.meta['derivative_id']
        cars_pch = json.loads(response.body)
        #
        # if "calculation" not in cars_pch:
        #     print("cars_pch:", cars_pch)
        #     input("Stop1")

        CarImageUrl = str()

        if "calculation" in str(cars_pch):
        # if "deposit" in cars_pch['calculation']['parameters']:
            try:
                customer_deposit = cars_pch['calculation']['parameters']['deposit']
            except:
                customer_deposit = cars_pch['calculation']['details']['firstMonthPayment']

            duration_of_agreement = cars_pch['calculation']['parameters']['periodOfMonths']

            retailer_deposit_contribution = cars_pch['calculation']['details']['depositContribution']
            monthly_payment = cars_pch['calculation']['details']['monthlyPayment']

            if "retailPrice" in cars_pch:
                on_the_road_price = cars_pch['calculation']['retailPrice']
            elif "p11dPrice" in cars_pch:
                on_the_road_price = cars_pch['calculation']['p11dPrice']

            # on_the_road_price = cars_pch['calculation']['retailPrice']
            total_amount_payable = cars_pch['calculation']['details']['totalAmountPayable']
            PurchaseActivationFee = cars_pch['calculation']['details']['optionToPurchaseFee']
            representative_apr = cars_pch['calculation']['details']['apr']
            fixed_intrest_rate = cars_pch['calculation']['details']['aer']
            amount_of_credit = cars_pch['calculation']['details']['amountFinanced']
            final_payment = cars_pch['calculation']['details']['finalPayment']
            excess_milage_charge = cars_pch['calculation']['parameters']['excessMileage']

            if "personal" in response.url:
                type_of_finance = "PCP"
                on_the_road_price = cars_pch['calculation']['retailPrice']
                WebpageURL = 'https://www.volkswagen.co.uk/finance-calculator#!/view/screen-2?annualMileage=10&periodOfMonths='+str(duration_of_agreement)+'&deposit='+str(customer_deposit)+'&modelId='+str(model_id)+'&trimId='+str(trim_id)+'&derivativeId='+derivative_id+'&pageIndex=0&customerType=personal&paymentBreakdown=deposit'
            else:
                type_of_finance = "BCH"
                on_the_road_price = cars_pch['calculation']['p11dPrice']
                WebpageURL = 'https://www.volkswagen.co.uk/finance-offers-and-fleet/finance-calculator#!/view/screen-2?servicePlan=NOPLAN&rentalsInAdvance=3&annualMileage=10&periodOfMonths='+str(duration_of_agreement)+'&modelId='+str(model_id)+'&trimId='+str(trim_id)+'&derivativeId='+derivative_id+'&pageIndex=0&productType=CONTRACT_HIRE'

            # if "product" in cars_pch:
            #     # print("cars_pch:", cars_pch)
            #     # input("Stop1")
            #     disclaimer = cars_pch['product']['disclaimer']
            #     offerExp = disclaimer.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
            #     OfferExpiryDate = self.dateMatcher(offerExp)[0]
            # else:
            #     OfferExpiryDate = str()
            OfferExpiryDate = '30/06/2022'
            # print("customer_deposit:", customer_deposit)
            # print("monthly_payment:", monthly_payment)
            # print("on_the_road_price:", on_the_road_price)
            # print("total_amount_payable:", total_amount_payable)
            # input("Stop1")


            average_miles_per_year = '10000'



            # if "Offer available when ordered by " in OfferExpiryDate:
            #     OfferExpiryDate = OfferExpiryDate.split('Offer available when ordered by ')[1]
            #     if " from participating" in OfferExpiryDate:
            #         OfferExpiryDate = OfferExpiryDate.split(" from participating")[0]
            # elif "Offer available for vehicles ordered by " in OfferExpiryDate:
            #     OfferExpiryDate = OfferExpiryDate.split('Offer available for vehicles ordered by ')[1]
            #     if " from participating" in OfferExpiryDate:
            #         OfferExpiryDate = OfferExpiryDate.split(" from participating")[0]
            # elif "Ordered by" in OfferExpiryDate:
            #     OfferExpiryDate = OfferExpiryDate.split('Ordered by')[1].split(" from participating")[0]
            # print("response: ", response.url)
            # print("OfferExpiryDate: ", OfferExpiryDate)
            # input("stop")

            if "up!" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/up-pa/hero/480/180.png'
            elif "New Polo" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/polo-nf/hero/480/180.png'
            elif "Beetle" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/beetle-pa/hero/480/180.png'
            elif "Scirocco" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/scirocco-gp/hero/480/180.png'
            elif "Golf" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/golf-vii-pa/hero/480/180.png'
            elif "T-Roc" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/troc/hero/480/180.png'
            elif "New Golf" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/golf-sv-pa/hero/480/180.png'
            elif "Beetle Cabriolet" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/beetle-cab-pa/hero/480/180.png'
            elif "Golf Estate" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/golf-estate-vii-pa/hero/480/180.png'
            elif "Passat" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/passat-viii/hero/480/180.png'
            elif "Tiguan" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/tiguan-nf/hero/480/180.png'
            elif "Touran" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/touran-nf/hero/480/180.png'
            elif "Passat Estate" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/passat-estate-viii/hero/480/180.png'
            elif "Sharan" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/sharan-fl/hero/480/180.png'
            elif "Tiguan Allspace" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/tiguan-allspace/hero/480/180.png'
            elif "Arteon" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/arteon/hero/480/180.png'
            elif "Touareg" in car_model:
                CarImageUrl = 'http://imagecom.volkswagen.co.uk/api/image/v2/360s/car/vw/touareg-fl/hero/480/180.png'

            if "calculation" in cars_pch:
                financeType = cars_pch['calculation']['productType']

                if "CONTRACT_HIRE" in financeType:
                    type_of_finance = 'Contract Hire'

                else:
                    type_of_finance = 'PCP'


                item = CarItem()
                item['CarMake'] = car_make
                item['CarModel'] = car_model
                item['TypeofFinance'] = self.get_type_of_finance(type_of_finance)
                item['MonthlyPayment'] = self.make_two_digit_no(str(monthly_payment))
                if item['MonthlyPayment']:
                    item['MonthlyPayment'] = float(item['MonthlyPayment'])
                item['CustomerDeposit'] = self.make_two_digit_no(str(customer_deposit))
                if item['CustomerDeposit']:
                    item['CustomerDeposit'] = float(item['CustomerDeposit'])
                item['RetailerDepositContribution'] = retailer_deposit_contribution
                if item['RetailerDepositContribution']:
                    item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
                item['OnTheRoadPrice'] = on_the_road_price
                if item['OnTheRoadPrice']:
                    item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
                item['AmountofCredit'] = amount_of_credit
                item['DurationofAgreement']   = self.remove_percentage_sign(str(duration_of_agreement))
                item['OptionalPurchase_FinalPayment']   = final_payment
                item['TotalAmountPayable'] = str(total_amount_payable).replace(",", "")
                item['OptionToPurchase_PurchaseActivationFee'] = PurchaseActivationFee
                item['RepresentativeAPR'] = self.remove_percentage_sign(str(representative_apr))
                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(str(fixed_intrest_rate))
                item['ExcessMilageCharge'] = self.remove_percentage_sign(str(excess_milage_charge))
                item['AverageMilesPerYear'] = self.remove_percentage_sign(average_miles_per_year)
                item['RetailCashPrice'] = on_the_road_price
                item['OfferExpiryDate'] = OfferExpiryDate
                # item['OfferExpiryDate'] = '31st March 2019'
                item['WebpageURL'] = WebpageURL
                item['CarimageURL'] = CarImageUrl
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                if item['MonthlyPayment'] != '':
                    yield item

            # print("url", response.url)
            # print("cars_pch: ", cars_pch)
            # print("paremet: ", cars_pch['calculation'])
            # input("stop")
