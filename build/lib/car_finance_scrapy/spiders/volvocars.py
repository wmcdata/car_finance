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
from scrapy.selector import Selector


class VolvocarsSpider(BaseSpider):
    name = "volvocars.com"

    allowed_domains = ['volvocars.com']
    handle_httpstatus_list = [403]

    # 'https://volvo-uk-financecalculator.azurewebsites.net/content/config/presets.js',
    start_url = ['https://www.volvocars.com/uk/cars/business-sales/business-offers', 'https://www.volvocars.com/uk/cars/offers?redirect=true']


    def __init__(self):
        super(VolvocarsSpider, self).__init__()

    def start_requests(self):
        for url  in self.start_url:
            yield Request(url, callback=self.parse_model_url, headers=self.headers_volvo, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com"})

    def parse_model_url(self, response):

        if "/cars/offers" in response.url:
            # offerExp = self.getTextAll(response, '//div[@class="extf-content"]/text()')
            # offerExp = offerExp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
            # OfferExpiryDate = self.dateMatcher(offerExp)[0]
            OfferExpiryDate = '30/06/2022'

            new_offer_urls = response.xpath('//div[contains(@id, "itemListSlider_")]//div[contains(@class, "item-list-item")]')
            for href in new_offer_urls:
                href = self.getText(href, "./a/@href")
                href = response.urljoin(href)
                # print("href", href)
                # input("stop 1")
                yield Request(href, callback=self.parse_new_model_url, dont_filter=True, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com", "OfferExpiryDate":OfferExpiryDate}, headers=self.headers_volvo)
        if "business-offers" in response.url:### BCH OFFERS
            offer_urls = response.xpath('//div[contains(@class, "item-list-item")]')
            for href in offer_urls:
                otr_price = self.getTextAll(href, ".//p[@class='body']//text()")
                url = self.getText(href, './/a/@href')
                href = response.urljoin(url)
                # print("url", response.url)
                # print("href", href)
                # print("otr_price", otr_price)
                # input("stop 1")
                yield Request(href, callback=self.parse_model_business, meta={"otr_price":otr_price, 'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com"}, headers=self.headers_volvo)
        # if "presets" in response.url: ### HP AND PHP
        #     # print("url", response.url)
        #     # print("url", href)
        #     # print("otr_price", otr_price)
        #     # input("stop")
        #     yield Request(response.url, callback=self.volvo_hp_offer_link, headers=self.headers, dont_filter=True)

    def parse_model_business(self, response):
        """BCH OFFERS
        """

        # offerExp = self.getTextAll(response, '//div[@id="terms"]//em/text()')
        # offerExp = offerExp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        # OfferExpiryDate = self.dateMatcher(offerExp)[0]
        OfferExpiryDate = '30/06/2022'

        roadPrice = response.meta["otr_price"]
        # print("offerExp", OfferExpiryDate)
        # input("stop")
        if "From" in roadPrice:
            ontheRoadPrice = roadPrice.split("From ")[1].split(" ")[0]
        else:
            ontheRoadPrice = 'N/A'

        # offer_text = self.getTextAll(response, '//div[@id="terms"]//em/text()')
        # all_date = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", offer_text)
        # OfferExpiryDate = all_date[1]
        # print("url", response.url)
        # # print("MonthlyPayment", item['MonthlyPayment'])
        # # print("CustomerDeposit", item['CustomerDeposit'])
        # # print("CarModel", th_name)
        # input("stop")

        idx = 1
        for th_name in response.xpath('//table[@class="features-table specs-table--header"]/thead/tr/th[//h4[contains(text(), "Business Contract Hire Offers")]]//following-sibling::th'):

            item = CarItem()
            item['CarMake'] = 'Volvo'
            modle = self.getTextAll(th_name, './/h5//text()')
            if "Diesel" not in modle and "Petrol" not in modle and "Recharge" not in modle:
                item['CarModel'] = modle
                # print("url", response.url)
                # print("CarModel", item['CarModel'])
                # input("stop")
                item['TypeofFinance'] = self.get_type_of_finance('Business Contract Hire')
                item['MonthlyPayment'] = self.make_two_digit_no(self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Monthly Rental', idx))))
                item['CustomerDeposit'] = self.make_two_digit_no(self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Initial Rental', idx))))
                item['RetailerDepositContribution'] = 'N/A'
                item['OnTheRoadPrice'] = item['RetailCashPrice'] = self.remove_gbp(ontheRoadPrice)
                item['OptionalPurchase_FinalPayment'] = 'N/A'
                item['AmountofCredit'] = 'N/A'
                DurationofAgreement = self.getTextAll(th_name, self.get_xpath('Contract Length', idx))
                item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                item['TotalAmountPayable'] = 'N/A'
                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                item['RepresentativeAPR'] = 'N/A'
                item['FixedInterestRate_RateofinterestPA'] = 'N/A'

                ExcessMilageCharge = self.getTextAll(th_name, self.get_xpath('Excess mileage charge', idx))
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                item['AverageMilesPerYear'] = self.remove_percentage_sign(self.getTextAll(th_name, self.get_xpath('Mileage per annum', idx)))
                item['OfferExpiryDate'] = OfferExpiryDate
                item['DebugMode'] = self.Debug_Mode

                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                item['CarimageURL'] = 'N/A'
                item['WebpageURL'] = response.url
                idx += 1
                if item['MonthlyPayment'] != '' and item['CarModel'] != '':
                    yield item



    def volvo_hp_offer_link(self, response):
        data_js = json.loads(response.body)
        data_model = data_js['models']
        for mod_loop in data_model: ### Model LOOP
            data_varient = mod_loop['variants']
            for var_loop in data_varient:  ### variants LOOP
                data_engine = var_loop['engines']
                for filter_data in data_engine: ### Engine LOOP
                    ShortName = filter_data['ShortName']
                    CapCode = filter_data['CapCode']
                    Model = filter_data['Model']
                    SalesName = filter_data['SalesName']
                    Transmission = filter_data['Transmission']
                    PriceGBP = str(filter_data['PriceGBP'])
                    Engine = filter_data['name']
                    deposit = '3000'
                    term = '36'
                    excessMill = '8000'

                    link = 'https://volvo-uk-financecalculator.azurewebsites.net/Quote/quote'
                    # Duration = ['36', '42', '48']
                    financeType = ['ConditionalSale', 'PersonalContractPurchase']

                    for financePlan in financeType:
                        if "ConditionalSale" in financePlan:
                            formdata = {
                                'Edited': 'False',
                                'Period': term,
                                'Rental': '0',
                                'Insurance': '0',
                                'WithMaintenance': 'False',
                                'VehicleDetails.CapId': '0',
                                'VehicleDetails.CapCode': CapCode,
                                'VehicleDetails.PriceGBP': PriceGBP,
                                'VehicleDetails.SalesName': SalesName,
                                'VehicleDetails.Transmission': Transmission,
                                'VehicleDetails.Model': Model,
                                'VehicleDetails.Engine': Engine,
                                'VehicleDetails.ShortName': ShortName,
                                'VehicleDetails.Plan': 'ConditionalSale',
                                'FinancePlan': 'ConditionalSale',
                                'Deposit': deposit
                                }
                        else:
                            formdata = {
                                'Edited': 'False',
                                'Period': term,
                                'Rental': '0',
                                'Insurance': '0',
                                'WithMaintenance': 'False',
                                'VehicleDetails.CapId': '0',
                                'VehicleDetails.CapCode': CapCode,
                                'VehicleDetails.PriceGBP': PriceGBP,
                                'VehicleDetails.SalesName': SalesName,
                                'VehicleDetails.Transmission': Transmission,
                                'VehicleDetails.Model': Model,
                                'VehicleDetails.Engine': Engine,
                                'VehicleDetails.ShortName': ShortName,
                                'VehicleDetails.Plan': 'PersonalContractPurchase',
                                'FinancePlan': 'PersonalContractPurchase',
                                'Deposit': deposit,
                                'EstimatedAnnualMileage': excessMill
                                }
                        # print("formdata: ", formdata)
                        # input("stop")
                        yield FormRequest(link, formdata=formdata, callback=self.parse_volvo_hp_items, headers=self.headers_volvo, meta={'proxy':"shp-watchmycompetitor-uk-v00001.tp-ns.com", 'model':Model, 'Engine':Engine, "SalesName":SalesName}, dont_filter=True)

    def parse_volvo_hp_items(self, response):
        """Conditional Sale AND PCP
        """
        model = response.meta['model']
        Engine = response.meta['Engine']
        car_SalesName = response.meta['SalesName']
        CarModel = model + " " + car_SalesName +" "+Engine
        MonthlyPayment = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Monthly payments")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        CustomerDeposit = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Customer Deposit")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        RetailerDepositContribution = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Finance Deposit Contribution")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        RepresentativeAPR = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Representative APR")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        OnTheRoadPrice = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "On the road price")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        AmountofCredit = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Amount of credit")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        TotalAmountPayable = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Total amount payable")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        DurationofAgreement = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Duration of agreement")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        FixedInterestRate_RateofinterestPA = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Fixed interest rate")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')

        AverageMilesPerYear = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Mileage per annum")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        ExcessMilageCharge = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Excess mileage charg")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')

        OptionalPurchase_FinalPayment = self.getText(response, '//div[@class="bur-calc-price-lines"]//div[contains(text(), "Optional Final Payment")]/following-sibling::div[@class="col-xs-6 bur-calc-item-right"]//text()')
        if OptionalPurchase_FinalPayment:
            TypeofFinance = 'Personal Contract Purchase'
        else:
            TypeofFinance = 'Conditional Sale'

        # print("url", response.url)
        # print("MonthlyPayment: ", MonthlyPayment)
        # # print("CustomerDeposit: ", CustomerDeposit)
        # print("RetailerDepositContribution: ", RetailerDepositContribution)
        # # print("RepresentativeAPR: ", RepresentativeAPR)
        # print("OnTheRoadPrice: ", OnTheRoadPrice)
        # # print("AmountofCredit: ", AmountofCredit)
        # # print("TotalAmountPayable: ", TotalAmountPayable)
        # # print("DurationofAgreement: ", DurationofAgreement)
        # # print("OptionalPurchase_FinalPayment: ", OptionalPurchase_FinalPayment)
        # input("stop")

        item = CarItem()
        item['CarMake'] = 'Volvo'
        item['CarModel'] = CarModel
        item['TypeofFinance'] = TypeofFinance
        item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
        if item['MonthlyPayment']:
            item['MonthlyPayment'] = float(item['MonthlyPayment'])
        item['CustomerDeposit'] = self.make_two_digit_no(self.remove_gbp(CustomerDeposit))
        if item['CustomerDeposit']:
            item['CustomerDeposit'] = float(item['CustomerDeposit'])
        item['RetailerDepositContribution'] = self.make_two_digit_no(self.remove_gbp(RetailerDepositContribution))
        item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
        item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
        item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
        item['OptionToPurchase_PurchaseActivationFee'] = ''
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
        item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
        item['OfferExpiryDate'] = 'N/A'
        item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
        item['CarimageURL'] = 'N/A'
        item['WebpageURL'] = 'https://volvo-uk-financecalculator.azurewebsites.net/Home/index'
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        if item['MonthlyPayment'] != '':
            yield item

    def parse_new_model_url(self, response):
        """Volvl NEW MODEL 40
        """
        # financePlan = self.getTexts(response, '//h4/text()')
        # for TypeofFinance in financePlan:
        #     # print("TypeofFinance: ", TypeofFinance)
        #     # input("stop")
        #     if "Personal Contract Hire" in TypeofFinance:
        OfferExpiryDate = response.meta['OfferExpiryDate']
        idx = 1
        for th_name in response.xpath('//table[@class="features-table specs-table--header"]/thead/tr/th[//h4[contains(text(), "Personal Contract Hire Offers")]]//following-sibling::th'):
            item = CarItem()
            item['CarMake'] = 'Volvo'
            modle = self.getTextAll(th_name, './/h5//text()')

            if "Diesel" not in modle and "Petrol" not in modle and "Recharge" not in modle:
                item['CarModel'] = modle
                item['TypeofFinance'] = self.get_type_of_finance('Personal Contract Hire')
                item['MonthlyPayment'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Monthly Rental', idx)))
                item['CustomerDeposit'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Initial Rental', idx)))
                item['RetailerDepositContribution'] = 'N/A'
                item['OnTheRoadPrice'] = item['RetailCashPrice'] = 'N/A'
                item['OptionalPurchase_FinalPayment'] = 'N/A'
                item['AmountofCredit'] = 'N/A'
                DurationofAgreement = self.getTextAll(th_name, self.get_xpath('Contract Length', idx))
                item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                item['TotalAmountPayable'] = 'N/A'
                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                item['RepresentativeAPR'] = 'N/A'
                item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                ExcessMilageCharge = self.getTextAll(th_name, self.get_xpath('Excess mileage charge', idx))
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                item['AverageMilesPerYear'] = self.remove_percentage_sign(self.getTextAll(th_name, self.get_xpath('Mileage per annum', idx)))
                item['OfferExpiryDate'] = OfferExpiryDate
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                item['CarimageURL'] = 'N/A'
                item['WebpageURL'] = response.url
                idx += 1
                if item['MonthlyPayment'] != '' and item['CarModel'] != '':
                    yield item

            # elif "Personal Contract Purchase":
        i = 0
        model = self.getTextAll(response, '//table[@class="features-table specs-table--header"]/thead/tr[th/h4[contains(text(), "Personal Contract Purchase ")]]//following-sibling::tr[2]//th//h5/text()')
        model = model.split("Model")[1].strip()
        CarModel = model.split(")")

        MonthlyPayment = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Monthly payments") or contains(text(), "monthly payments")]/following-sibling::td//text()').extract()
        CustomerDeposit = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Customer deposit") or contains(text(), "Customer Deposit")]/following-sibling::td//text()').extract()
        RetailerDepositContribution = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Finance Deposit Contribution") or contains(text(), "Finance deposit contribution")]/following-sibling::td//text()').extract()
        RepresentativeAPR = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "APR")]/following-sibling::td//text()').extract()
        OnTheRoadPrice = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Revised on the road price")]/following-sibling::td//text()').extract()
        AmountofCredit = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Amount of credit") or contains(text(), "Amount of Credit")]/following-sibling::td//text()').extract()
        TotalAmountPayable = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td//text()').extract()
        OptionalPurchase_FinalPayment = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Optional final payment") or contains(text(), "Optional Final Payment")]/following-sibling::td//text()').extract()
        DurationofAgreement = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Duration of agreement (months)")]/following-sibling::td//text()').extract()
        FixedInterestRate_RateofinterestPA = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Fixed rate of interest p.a")]/following-sibling::td//text()').extract()
        AverageMilesPerYear = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Mileage per annum")]/following-sibling::td//text()').extract()
        ExcessMilageCharge = response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Excess mileage charge")]/following-sibling::td//text()').extract()


        # if "-models/s60/off" in response.url:
        # print("MonthlyPayment: ", MonthlyPayment)
        # # print("CustomerDeposit: ", CustomerDeposit)
        # print("RetailerDepositContribution: ", RetailerDepositContribution)
        # print("OnTheRoadPrice: ", OnTheRoadPrice)
        # # print("AmountofCredit: ", AmountofCredit)
        # # print("TotalAmountPayable: ", TotalAmountPayable)
        # # print("DurationofAgreement: ", DurationofAgreement)
        # # print("model: ", CarModel)
        # print("resp: ", response.url)
        # input("stop")

        for x in range(len(MonthlyPayment)):

            item = CarItem()
            item['CarMake'] = 'Volvo'
            item['CarModel'] = CarModel[i]+")"
            item['TypeofFinance'] = self.get_type_of_finance('Personal Contract Purchase')
            item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment[i])
            item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit[i])
            if RetailerDepositContribution[i] == '£0' or RetailerDepositContribution[i] == '':
                item['RetailerDepositContribution'] = self.remove_gbp(response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "Retailer contribution") or contains(text(), "Retailer Contribution")]/following-sibling::td//text()').extract()[i])
            else:
                item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution[i])

            if OnTheRoadPrice[i]:
                item['OnTheRoadPrice'] = item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice[i])
            elif OnTheRoadPrice[i] == "0" or OnTheRoadPrice[i] == '':
                item['OnTheRoadPrice'] = item['RetailCashPrice'] = self.remove_gbp(response.xpath('//table[@class="features-table"]/tbody/tr/td[contains(text(), "On the road price")]/following-sibling::td//text()').extract()[i])
            else:
                item['OnTheRoadPrice'] = item['RetailCashPrice'] = 'N/A'
            if OptionalPurchase_FinalPayment[i]:
                item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment[i])
            else:
                item['OptionalPurchase_FinalPayment'] = 'N/A'
            if AmountofCredit[i]:
                item['AmountofCredit'] = self.remove_gbp(AmountofCredit[i])
            else:
                item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement[i])
            if TotalAmountPayable[i]:
                item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable[i])
            else:
                item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = self.remove_percentage_sign(self.remove_gbp(RepresentativeAPR[i]))
            item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(self.remove_gbp(FixedInterestRate_RateofinterestPA[i]))
            item['ExcessMilageCharge'] = self.remove_percentage_sign(self.remove_gbp(ExcessMilageCharge[i]))
            item['AverageMilesPerYear'] = self.remove_percentage_sign(self.remove_gbp(AverageMilesPerYear[i]))
            item['OfferExpiryDate'] = OfferExpiryDate
            item['DebugMode'] = self.Debug_Mode
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            item['CarimageURL'] = 'N/A'
            item['WebpageURL'] = response.url
            i += 1
            if item['MonthlyPayment'] != '' and item['CarModel'] != '':
                yield item

        # offer_text = self.getText(response, '//div[@id="terms"]//em[contains(text(), "vehicles registered by")]/text()')
        # OfferExpiryDate = offer_text.split("vehicles registered by ")[1].split(".")[0]
        # OfferExpiryDate = offer_date.split("to")[1]


        # idx = 1
        # # body = response.body.decode('utf-8')
        # # model = self.reText(body, r'"site_segment":"([^"]+)"').upper()
        # for th_name in response.xpath('//table[@class="features-table specs-table--header"]/thead/tr/th/*[contains(text(), "Personal Contract Purchase")]/../following-sibling::th'):
        #     item = CarItem()
        #     item['CarMake'] = 'Volvo'
        #     item['CarModel'] = self.getText(th_name, './h5/text()')
        #     if model not in item['CarModel']:
        #         item['CarModel'] = model + ' ' + item['CarModel']
        #     item['TypeofFinance'] = self.get_type_of_finance('PCP')
        #     item['MonthlyPayment'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('onthly payments', idx)))
        #     if item['MonthlyPayment']:
        #         item['MonthlyPayment'] = float(item['MonthlyPayment'])
        #     item['CustomerDeposit'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Customer deposit', idx)))
        #     if item['CustomerDeposit']:
        #         item['CustomerDeposit'] = float(item['CustomerDeposit'])
        #     item['RetailerDepositContribution'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Finance Deposit Contribution', idx)))
        #     if item['RetailerDepositContribution'] == '':
        #         item['RetailerDepositContribution'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Finance deposit contribution', idx)))
        #     if item['RetailerDepositContribution']:
        #         item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
        #     item['OnTheRoadPrice'] = item['RetailCashPrice'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Revised on the road price', idx)))
        #     item['OptionalPurchase_FinalPayment'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('final payment', idx)))
        #     if item['OptionalPurchase_FinalPayment'] == '':
        #         item['OptionalPurchase_FinalPayment'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Final Payment', idx)))
        #     item['AmountofCredit'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Amount of Credit', idx)))
        #     if item['AmountofCredit'] == '':
        #         item['AmountofCredit'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Amount of credit', idx)))
        #     item['DurationofAgreement'] = self.getTextAll(th_name, self.get_xpath('Duration of agreement', idx))
        #     item['TotalAmountPayable'] = self.remove_gbp(self.getTextAll(th_name, self.get_xpath('Total amount payable', idx)))
        #     #item['OptionToPurchase_PurchaseActivationFee'] = self.getTextAll(th_name, self.get_xpath('Revised on the road price', idx))
        #     RepresentativeAPR = self.getText(th_name, self.get_xpath('APR', idx))
        #     if "APR" in RepresentativeAPR:
        #         RepresentativeAPR = RepresentativeAPR.split("APR")[0]
        #     item['RepresentativeAPR'] = RepresentativeAPR
        #     item['OptionToPurchase_PurchaseActivationFee'] = ''
        #     item['FixedInterestRate_RateofinterestPA'] = self.getTextAll(th_name, self.get_xpath('rate of interest', idx))
        #     ExcessMilageCharge = self.getTextAll(th_name, self.get_xpath('Excess mileage charge', idx))
        #     if "p" in ExcessMilageCharge:
        #         ExcessMilageCharge = ExcessMilageCharge.split("p")[0]
        #     item['ExcessMilageCharge'] = ExcessMilageCharge
        #     # item['OfferExpiryDate'] = OfferExpiryDate
        #     item['OfferExpiryDate'] = 'N/A'
        #     item['AverageMilesPerYear'] = self.getTextAll(th_name, self.get_xpath('Mileage per annum', idx))
        #     item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        #     try:
        #         item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        #     except:
        #         item['DepositPercent'] = float()
        #     src = th_name.xpath('./../../../../../../preceding-sibling::div[1]//div[@class="extf-scale"]/img/@src').extract_first()
        #     if src != '' and src != None:
        #         item['CarimageURL'] = response.urljoin(src.split('?')[0])
        #     item['WebpageURL'] = response.url
        #     item['DebugMode'] = self.Debug_Mode
        #     idx += 1
        #     yield item


    #     if "/cars/new-models/xc40/offers" in response.url:
    #
    #         carMake = 'Volvo'
    #         item = CarItem()
    #         item['CarMake'] = carMake
    #         item['CarModel'] = "XC40 T3 Momentum Front Wheel Drive Manual (Metallic Paint Included)"
    #         item['TypeofFinance'] = "Personal Contract Purchase"
    #         item['MonthlyPayment'] = "299"
    #         item['CustomerDeposit'] = "4903.19"
    #         item['RetailerDepositContribution'] = '0'
    #         item['OnTheRoadPrice'] = '30170'
    #         item['AmountofCredit'] = '23846.81'
    #         item['DurationofAgreement'] = '49'
    #         item['OptionalPurchase_FinalPayment'] = '13966.88'
    #         item['TotalAmountPayable'] = '33222.07'
    #         item['OptionToPurchase_PurchaseActivationFee'] = ''
    #         item['RepresentativeAPR'] = '5.9%'
    #         item['FixedInterestRate_RateofinterestPA'] = '3.04'
    #         item['ExcessMilageCharge'] = '14.9'
    #         item['AverageMilesPerYear'] = '10000'
    #         item['OfferExpiryDate'] = '30/09/2020'
    #         item['RetailCashPrice'] = '30170'
    #         item['DebugMode'] = self.Debug_Mode
    #         item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc40/offers?redirect=true'
    #         item['CarimageURL'] = ''
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
    #         yield item
    #         # print("volvocars.com", response.url)
    #         # print("volvocars.com", item)
    #         # input("stop")
    #         carMake = 'Volvo'
    #         item = CarItem()
    #         item['CarMake'] = carMake
    #         item['CarModel'] = "XC40 T3 R-Design Front Wheel Drive Manual (Metallic Paint Included)"
    #         item['TypeofFinance'] = "Personal Contract Purchase"
    #         item['MonthlyPayment'] = "319"
    #         item['CustomerDeposit'] = "4844.92"
    #         item['RetailerDepositContribution'] = '0'
    #         item['OnTheRoadPrice'] = '32045'
    #         item['AmountofCredit'] = '25686.33'
    #         item['DurationofAgreement'] = '49'
    #         item['OptionalPurchase_FinalPayment'] = '15210.00'
    #         item['TotalAmountPayable'] = '35366.92'
    #         item['OptionToPurchase_PurchaseActivationFee'] = ''
    #         item['RepresentativeAPR'] = '5.9%'
    #         item['FixedInterestRate_RateofinterestPA'] = '3.04'
    #         item['ExcessMilageCharge'] = '14.9'
    #         item['AverageMilesPerYear'] = '10000'
    #         item['OfferExpiryDate'] = '30/09/2020'
    #         item['RetailCashPrice'] = '32045'
    #         item['DebugMode'] = self.Debug_Mode
    #         item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc40/offers?redirect=true'
    #         item['CarimageURL'] = ''
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
    #         yield item
    #
    #         carMake = 'Volvo'
    #         item = CarItem()
    #         item['CarMake'] = carMake
    #         item['CarModel'] = "XC40 D3 Momentum Front Wheel Drive Manual (Metallic Paint Included)"
    #         item['TypeofFinance'] = "Personal Contract Purchase"
    #         item['MonthlyPayment'] = "299"
    #         item['CustomerDeposit'] = "6872.86"
    #         item['RetailerDepositContribution'] = '0'
    #         item['OnTheRoadPrice'] = '32020'
    #         item['AmountofCredit'] = '23634.64'
    #         item['DurationofAgreement'] = '49'
    #         item['OptionalPurchase_FinalPayment'] = '13698.75'
    #         item['TotalAmountPayable'] = '34923.61'
    #         item['OptionToPurchase_PurchaseActivationFee'] = ''
    #         item['RepresentativeAPR'] = '5.9%'
    #         item['FixedInterestRate_RateofinterestPA'] = '3.04'
    #         item['ExcessMilageCharge'] = '14.9'
    #         item['AverageMilesPerYear'] = '10000'
    #         item['OfferExpiryDate'] = '30/09/2020'
    #         item['RetailCashPrice'] = '32020'
    #         item['DebugMode'] = self.Debug_Mode
    #         item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc40/offers?redirect=true'
    #         item['CarimageURL'] = ''
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
    #         yield item
    #
    #         carMake = 'Volvo'
    #         item = CarItem()
    #         item['CarMake'] = carMake
    #         item['CarModel'] = "XC40 T5 R-Design Plug-in hybrid Front Wheel Drive Automatic (Metallic Paint Included)"
    #         item['TypeofFinance'] = "Personal Contract Purchase"
    #         item['MonthlyPayment'] = "449"
    #         item['CustomerDeposit'] = "5742.50"
    #         item['RetailerDepositContribution'] = '0'
    #         item['OnTheRoadPrice'] = '41480'
    #         item['AmountofCredit'] = '34586.50'
    #         item['DurationofAgreement'] = '49'
    #         item['OptionalPurchase_FinalPayment'] = '17184.38'
    #         item['TotalAmountPayable'] = '44478.88'
    #         item['OptionToPurchase_PurchaseActivationFee'] = ''
    #         item['RepresentativeAPR'] = '5.9%'
    #         item['FixedInterestRate_RateofinterestPA'] = '3.04'
    #         item['ExcessMilageCharge'] = '14.9'
    #         item['AverageMilesPerYear'] = '10000'
    #         item['OfferExpiryDate'] = '30/09/2020'
    #         item['RetailCashPrice'] = '41480'
    #         item['DebugMode'] = self.Debug_Mode
    #         item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc40/offers?redirect=true'
    #         item['CarimageURL'] = ''
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
    #         yield item
    # ###################################333
    # ##############################3  CONTRACT HIRE
    # ################################################333
    #         carMake = 'Volvo'
    #         item = CarItem()
    #         item['CarMake'] = carMake
    #         item['CarModel'] = "XC40 T3 FWD Momentum Manual Metallic "
    #         item['TypeofFinance'] = "Personal Contract Hire"
    #         item['MonthlyPayment'] = "299"
    #         item['CustomerDeposit'] = "2155"
    #         item['RetailerDepositContribution'] = ''
    #         item['OnTheRoadPrice'] = ''
    #         item['AmountofCredit'] = ''
    #         item['DurationofAgreement'] = '48'
    #         item['OptionalPurchase_FinalPayment'] = ''
    #         item['TotalAmountPayable'] = ''
    #         item['OptionToPurchase_PurchaseActivationFee'] = ''
    #         item['RepresentativeAPR'] = ''
    #         item['FixedInterestRate_RateofinterestPA'] = ''
    #         item['ExcessMilageCharge'] = '13.8'
    #         item['AverageMilesPerYear'] = '10000'
    #         item['OfferExpiryDate'] = '30/09/2020'
    #         item['RetailCashPrice'] = ''
    #         item['DebugMode'] = self.Debug_Mode
    #         item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc40/offers?redirect=true'
    #         item['CarimageURL'] = ''
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
    #         yield item
    #
    #         carMake = 'Volvo'
    #         item = CarItem()
    #         item['CarMake'] = carMake
    #         item['CarModel'] = "XC40 T3 FWD R-Design Manual Metallic"
    #         item['TypeofFinance'] = "Personal Contract Hire"
    #         item['MonthlyPayment'] = "319"
    #         item['CustomerDeposit'] = "2091"
    #         item['RetailerDepositContribution'] = ''
    #         item['OnTheRoadPrice'] = ''
    #         item['AmountofCredit'] = ''
    #         item['DurationofAgreement'] = '48'
    #         item['OptionalPurchase_FinalPayment'] = ''
    #         item['TotalAmountPayable'] = ''
    #         item['OptionToPurchase_PurchaseActivationFee'] = ''
    #         item['RepresentativeAPR'] = ''
    #         item['FixedInterestRate_RateofinterestPA'] = ''
    #         item['ExcessMilageCharge'] = '13.8'
    #         item['AverageMilesPerYear'] = '10000'
    #         item['OfferExpiryDate'] = '30/09/2020'
    #         item['RetailCashPrice'] = ''
    #         item['DebugMode'] = self.Debug_Mode
    #         item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc40/offers?redirect=true'
    #         item['CarimageURL'] = ''
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
    #         yield item
    #
    #         carMake = 'Volvo'
    #         item = CarItem()
    #         item['CarMake'] = carMake
    #         item['CarModel'] = "XC40 T3 FWD R-Design Manual Metallic"
    #         item['TypeofFinance'] = "Personal Contract Hire"
    #         item['MonthlyPayment'] = "299"
    #         item['CustomerDeposit'] = "4088"
    #         item['RetailerDepositContribution'] = ''
    #         item['OnTheRoadPrice'] = ''
    #         item['AmountofCredit'] = ''
    #         item['DurationofAgreement'] = '48'
    #         item['OptionalPurchase_FinalPayment'] = ''
    #         item['TotalAmountPayable'] = ''
    #         item['OptionToPurchase_PurchaseActivationFee'] = ''
    #         item['RepresentativeAPR'] = ''
    #         item['FixedInterestRate_RateofinterestPA'] = ''
    #         item['ExcessMilageCharge'] = '13.8'
    #         item['AverageMilesPerYear'] = '10000'
    #         item['OfferExpiryDate'] = '30/09/2020'
    #         item['RetailCashPrice'] = ''
    #         item['DebugMode'] = self.Debug_Mode
    #         item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc40/offers?redirect=true'
    #         item['CarimageURL'] = ''
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
    #         yield item
    #
    #         carMake = 'Volvo'
    #         item = CarItem()
    #         item['CarMake'] = carMake
    #         item['CarModel'] = "XC40 T4 FWD R-Design Plug-in hybrid Automatic Metallic"
    #         item['TypeofFinance'] = "Personal Contract Hire"
    #         item['MonthlyPayment'] = "449"
    #         item['CustomerDeposit'] = "2887"
    #         item['RetailerDepositContribution'] = ''
    #         item['OnTheRoadPrice'] = ''
    #         item['AmountofCredit'] = ''
    #         item['DurationofAgreement'] = '48'
    #         item['OptionalPurchase_FinalPayment'] = ''
    #         item['TotalAmountPayable'] = ''
    #         item['OptionToPurchase_PurchaseActivationFee'] = ''
    #         item['RepresentativeAPR'] = ''
    #         item['FixedInterestRate_RateofinterestPA'] = ''
    #         item['ExcessMilageCharge'] = '13.8'
    #         item['AverageMilesPerYear'] = '10000'
    #         item['OfferExpiryDate'] = '30/09/2020'
    #         item['RetailCashPrice'] = ''
    #         item['DebugMode'] = self.Debug_Mode
    #         item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc40/offers?redirect=true'
    #         item['CarimageURL'] = ''
    #         item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
    #         item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
    #         yield item

##########################################################
#########################
####################################################################################
        # if "cars/new-models/xc90" in response.url:
        #     carMake = 'Volvo'
        #     item = CarItem()
        #     item['CarMake'] = carMake
        #     item['CarModel'] = "XC90 B5 Momentum All Wheel Drive Automatic (Metallic Paint Included)"
        #     item['TypeofFinance'] = "PCP"
        #     item['MonthlyPayment'] = "507.35"
        #     item['CustomerDeposit'] = "10106.00"
        #     item['RetailerDepositContribution'] = '0'
        #     item['OnTheRoadPrice'] = '50527.37'
        #     item['AmountofCredit'] = '40421.37'
        #     item['DurationofAgreement'] = '37'
        #     item['OptionalPurchase_FinalPayment'] = '22156.88'
        #     item['TotalAmountPayable'] = '50527.37'
        #     item['OptionToPurchase_PurchaseActivationFee'] = ''
        #     item['RepresentativeAPR'] = '0%'
        #     item['FixedInterestRate_RateofinterestPA'] = ''
        #     item['ExcessMilageCharge'] = '14.9'
        #     item['AverageMilesPerYear'] = '10000'
        #     item['OfferExpiryDate'] = '30/09/2020'
        #     item['RetailCashPrice'] = '50527.37'
        #     item['DebugMode'] = self.Debug_Mode
        #     item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc90/offers?redirect=true'
        #     item['CarimageURL'] = ''
        #     item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        #     item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        #     yield item
        #
        #     carMake = 'Volvo'
        #     item = CarItem()
        #     item['CarMake'] = carMake
        #     item['CarModel'] = "XC90 B5 R-Design All Wheel Drive Automatic (Metallic Paint Included)"
        #     item['TypeofFinance'] = "PCP"
        #     item['MonthlyPayment'] = "509.45"
        #     item['CustomerDeposit'] = "10728.00"
        #     item['RetailerDepositContribution'] = '0'
        #     item['OnTheRoadPrice'] = '53638.37'
        #     item['AmountofCredit'] = '42910.37'
        #     item['DurationofAgreement'] = '37'
        #     item['OptionalPurchase_FinalPayment'] = '24570.00'
        #     item['TotalAmountPayable'] = '53638.37'
        #     item['OptionToPurchase_PurchaseActivationFee'] = ''
        #     item['RepresentativeAPR'] = '0%'
        #     item['FixedInterestRate_RateofinterestPA'] = ''
        #     item['ExcessMilageCharge'] = '14.9'
        #     item['AverageMilesPerYear'] = '10000'
        #     item['OfferExpiryDate'] = '30/09/2020'
        #     item['RetailCashPrice'] = '53638.37'
        #     item['DebugMode'] = self.Debug_Mode
        #     item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc90/offers?redirect=true'
        #     item['CarimageURL'] = ''
        #     item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        #     item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        #     yield item
        #
        #     carMake = 'Volvo'
        #     item = CarItem()
        #     item['CarMake'] = carMake
        #     item['CarModel'] = "XC90 B5 Momentum All Wheel Drive Automatic (Metallic Paint Included)"
        #     item['TypeofFinance'] = "PCP"
        #     item['MonthlyPayment'] = "534.58"
        #     item['CustomerDeposit'] = "10120.00"
        #     item['RetailerDepositContribution'] = '0'
        #     item['OnTheRoadPrice'] = '50595.62'
        #     item['AmountofCredit'] = '40475.62'
        #     item['DurationofAgreement'] = '37'
        #     item['OptionalPurchase_FinalPayment'] = '21230.63'
        #     item['TotalAmountPayable'] = '50595.62'
        #     item['OptionToPurchase_PurchaseActivationFee'] = ''
        #     item['RepresentativeAPR'] = '0%'
        #     item['FixedInterestRate_RateofinterestPA'] = ''
        #     item['ExcessMilageCharge'] = '14.9'
        #     item['AverageMilesPerYear'] = '10000'
        #     item['OfferExpiryDate'] = '30/09/2020'
        #     item['RetailCashPrice'] = '50595.62'
        #     item['DebugMode'] = self.Debug_Mode
        #     item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc90/offers?redirect=true'
        #     item['CarimageURL'] = ''
        #     item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        #     item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        #     yield item
        #
        #     carMake = 'Volvo'
        #     item = CarItem()
        #     item['CarMake'] = carMake
        #     item['CarModel'] = "XC90 T8 R-Design Plug-in hybrid All Wheel Drive Automatic (Metallic Paint Included)"
        #     item['TypeofFinance'] = "PCP"
        #     item['MonthlyPayment'] = "659.00"
        #     item['CustomerDeposit'] = "9787.34"
        #     item['RetailerDepositContribution'] = '3250'
        #     item['OnTheRoadPrice'] = '64185.50'
        #     item['AmountofCredit'] = '51148.16'
        #     item['DurationofAgreement'] = '49'
        #     item['OptionalPurchase_FinalPayment'] = '27251.25'
        #     item['TotalAmountPayable'] = '71920.59'
        #     item['OptionToPurchase_PurchaseActivationFee'] = ''
        #     item['RepresentativeAPR'] = '0%'
        #     item['FixedInterestRate_RateofinterestPA'] = ''
        #     item['ExcessMilageCharge'] = '14.9'
        #     item['AverageMilesPerYear'] = '10000'
        #     item['OfferExpiryDate'] = '30/09/2020'
        #     item['RetailCashPrice'] = '64185.50'
        #     item['DebugMode'] = self.Debug_Mode
        #     item['WebpageURL'] = 'https://www.volvocars.com/uk/cars/new-models/xc90/offers?redirect=true'
        #     item['CarimageURL'] = ''
        #     item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        #     item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
        #     yield item

            ##################################3
            ##################################333
            #################################3







    def get_xpath(self, text, index):
        return './../../../../following-sibling::ul//table//tr/td[contains(text(), "%s")]/following-sibling::td[%s]//text()' % (text, str(index))
