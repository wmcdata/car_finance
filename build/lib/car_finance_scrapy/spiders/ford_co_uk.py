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


class FordSpider(BaseSpider):

    DOWNLOAD_DELAY = 0.25
    name = "ford.co.uk"
    allowed_domains = ['ford.co.uk', 'serviceseucache.ford.com']
    start_url = 'https://www.ford.co.uk/shop/price-and-locate/promotions/personal'
    headers={'User-Agent': 'Pixray-Seeker/1.1 (Pixray-Seeker; http://www.pixray.com/pixraybot; crawler@pixray.com)'}
    def start_requests(self):
        yield Request(self.start_url, callback=self.parse_items, headers=self.headers)

    def parse_items(self, response):
        car_types=['new-fiesta','fiesta-promotions', 'fiesta-st','ecosport','puma','focus-promotions', 'focus','new-focus-st','tourneo-connect','new-kuga-promotions','mondeo','mustang-promotions','s-max','galaxy','tourneo-custom']
        for car_type in car_types:
            get_request_url='https://www.ford.co.uk/cars/'+car_type+'/promotions/personal.showroom'
            yield Request(get_request_url, callback=self.car_details_personal, headers=self.headers)
        for car_type in car_types:
            get_request_url='https://www.ford.co.uk/cars/'+car_type+'/promotions/business.showroom'
            yield Request(get_request_url, callback=self.car_details_business, headers=self.headers)
    def car_details_business(self,response):
        data_record=response.xpath('//div[@class="accordion accordion-showroom-offers"]/ul/li')
        for record in data_record:
            title=record.xpath('./div[@class="accordion-title"]/a/h3/text()').get()
            # print(title)
            # print(response.url)
            monthly_price=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/h2/text()').get()
            monthly_price=monthly_price.split(' ')[0]
            # monthly_price=monthly_price.lstrip('£')
            record_data=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/p/text()').get()
            expiry_date=record_data.split(',')[0].lstrip('Until').strip()
            car_model=record_data.split(',')[1].split('from')[0].strip().lstrip('you can drive away in the').strip()
            record_data_list=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/p[1]//text()').extract()
            record_data_list=" ".join(record_data_list)
            # print("record_data_list",record_data_list)
            # print("URL",response.url)
            # input("wait")
            duration=record_data_list.replace("per month on","per month over")
            duration=duration.split('per month over')[1].strip().split(' ')[0]
            duration=(int(duration))*12
                
            
            # print("duration",duration)
            # print("URL",response.url)
            # input("wait")
            # print('title->',title)
            # print('monthly_price->',monthly_price)
            # print('expiry_date->',expiry_date)
            # print('car_model->',car_model)
            # print('duration->',duration)
            # print(record_data_list)
            # print(duration)
            carMake = 'Ford'
            item = CarItem()
            item['CarMake'] = carMake
            item['CarModel'] = car_model
            if 'tourneo' in car_model.lower():
                item['TypeofFinance'] = "Commercial Contract Hire"
            else:
                item['TypeofFinance'] = "Contract Hire"
            item['MonthlyPayment'] = self.remove_gbp(monthly_price)
            item['CustomerDeposit'] = 'N/A'
            item['RetailerDepositContribution'] = 'N/A'
            item['OnTheRoadPrice'] = 'N/A'
            item['AmountofCredit'] = 'N/A'
            item['DurationofAgreement'] = duration
            item['OptionalPurchase_FinalPayment'] = 'N/A'
            item['TotalAmountPayable'] = 'N/A'
            item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
            item['RepresentativeAPR'] = 'N/A'
            item['FixedInterestRate_RateofinterestPA'] = 'N/A'
            item['ExcessMilageCharge'] = 'N/A'
            item['AverageMilesPerYear'] ='10000'
            item['OfferExpiryDate'] = expiry_date
            item['RetailCashPrice'] = 'N/A'
            item['DebugMode'] = self.Debug_Mode
            item['WebpageURL'] = response.url
            item['CarimageURL'] = 'https://www.gpas-cache.ford.com/guid/9366323c-63dd-3d73-9979-b9f1e3703f10.png'
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
            yield item
            
    def car_details_personal(self,response):
        # print("res", response.url)
        # input("wait")
        data_record=response.xpath('//div[@class="accordion accordion-showroom-offers"]/ul/li')
        for record in data_record:
            title=record.xpath('.//div[@class="accordion-title"]/a/h3/text()').get()
            record_body=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/p//text()').get()
            
            car_model=record_body.split('available')[0]
            car_model=car_model.split(',')[1]
            car_model=car_model.strip()
            car_model=car_model.rstrip('is')
            car_model=car_model.rstrip('are')
            car_model=car_model.lstrip('the')
            car_model=car_model.lstrip('selected')
            car_model=car_model.lstrip('a')
            
            
            date=record_body.split(',')[0].lstrip('Until')
            date=date.strip()
            vehicle_cash_price=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Cash Price")]/following-sibling::li/text()').get()
            if vehicle_cash_price is None:
                vehicle_cash_price='N/A'
            customer_deposit=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Customer Deposit")]/following-sibling::li/text()').get()
            if customer_deposit is None:
                customer_deposit='N/A'
            monthly_deposit=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Monthly Payments")]/following-sibling::li/text()').get()
            if monthly_deposit is None:
                monthly_deposit='N/A'
                duration='N/A'
            else:
                duration=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Monthly Payments")]/text()').get()
                duration=duration.split(' ')[0]
                
            optional_final_payment=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Final Payment")]/following-sibling::li/text()').get()
            if optional_final_payment is None:
                optional_final_payment='N/A'
            mileage_per_year=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"per annum") or contains(text(),"Per Annum")]/following-sibling::li/text()').get()
            if mileage_per_year is None:
                mileage_per_year='N/A'
            
            apr_percentage=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/h2/span/strong[contains(text(),"APR")]/text()').get()
            if apr_percentage is None:
                apr_percentage=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/h2/strong/span[contains(text(),"APR")]/text()').get()
            
            if apr_percentage is not None:
                apr_percentage=apr_percentage.split(' ')[0]
            else:
                apr_percentage='N/A'
            
            amount_of_credits=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Amount of Credit")]/following-sibling::li/text()').get()
            if amount_of_credits is None:
                amount_of_credits='N/A'
            purchase_fee=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Purchase Fee")]/following-sibling::li/text()').get()
            if purchase_fee is None:
                purchase_fee='N/A'
            amount_payable_by_customer=record.xpath('./div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"payable by customer")]/following-sibling::li/text()').get()
            if amount_payable_by_customer is None:
                amount_payable_by_customer='N/A'
            excess_mileage_charge=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"mileage charge")]/following-sibling::li/text()').get()
            if excess_mileage_charge is None:
                excess_mileage_charge='N/A'
            borrowing_rate=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Borrowing Rate")]/following-sibling::li/text()').get()
            if borrowing_rate is None:
                    borrowing_rate='N/A'
                    borrowing_rate='N/A'
            RetailerDepositContribution=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]//p/span/strong[contains(text(),"Deposit Allowance")]/text()').get()
            if RetailerDepositContribution is None:
                 RetailerDepositContribution=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]//p/strong/span[contains(text(),"Deposit Allowance")]/text()').get()
           
            if RetailerDepositContribution is None:
                RetailerDepositContribution='N/A'
            if RetailerDepositContribution is not None:
                RetailerDepositContribution=RetailerDepositContribution.split(' ')[0]
            if monthly_deposit!='N/A':
                if borrowing_rate!='N/A':
                    apr_percentage=record.xpath('.//div[@class="accordion-body"]//div[@class="box section"]//div[@class="regular  richtext-inner"]/ul/li[contains(text(),"Representative APR")]/following-sibling::li/text()').get()
                    # print('apr_percentage->',apr_percentage)
                else:
                    apr_percentage=apr_percentage
                #     print('apr_percentage->',apr_percentage)
                # print('url->',response.url)
                # print('title->',title)
                # print('car_model->',car_model)
                # print('date->',date)
                # print('vehicle_cash_price->',vehicle_cash_price)
                # print('customer_deposit->',customer_deposit)
                # print('monthly_deposit->',monthly_deposit)
                # print('optional_final_payment->',optional_final_payment)
                # print('mileage_per_year->',mileage_per_year)
                # print('Duration->',duration)
                
                # print('amount_of_credits->',amount_of_credits)
                # print('purchase_fee->',purchase_fee)
                # print('amount_payable_by_customer->',amount_payable_by_customer)
                # print('excess_mileage_charge->',excess_mileage_charge)
                # print('borrowing_rate->',borrowing_rate)
               
                """Items list
                """
                carMake = 'Ford'
                item = CarItem()
                item['CarMake'] = carMake
                item['CarModel'] = car_model
                if 'tourneo' in car_model.lower():
                    item['TypeofFinance'] = "Commercial Contract Hire"
                else:
                    item['TypeofFinance'] = "Personal Contract Purchase"
                item['MonthlyPayment'] = self.remove_gbp(monthly_deposit)
                item['CustomerDeposit'] = self.remove_gbp(customer_deposit)
                item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
                item['OnTheRoadPrice'] = self.remove_gbp(vehicle_cash_price)
                item['AmountofCredit'] = self.remove_gbp(amount_of_credits)
                item['DurationofAgreement'] = duration
                item['OptionalPurchase_FinalPayment'] = self.remove_gbp(optional_final_payment)
                item['TotalAmountPayable'] = self.remove_gbp(amount_payable_by_customer)
                item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(purchase_fee)
                item['RepresentativeAPR'] = apr_percentage
                item['FixedInterestRate_RateofinterestPA'] = self.remove_gbp(borrowing_rate)
                item['ExcessMilageCharge'] = self.remove_gbp(excess_mileage_charge)
                item['AverageMilesPerYear'] = mileage_per_year
                item['OfferExpiryDate'] = date
                item['RetailCashPrice'] = self.remove_gbp(vehicle_cash_price)
                item['DebugMode'] = self.Debug_Mode
                item['WebpageURL'] = response.url
                item['CarimageURL'] = 'https://www.gpas-cache.ford.com/guid/9366323c-63dd-3d73-9979-b9f1e3703f10.png'
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                item['DepositPercent'] =  self.get_percent(item['RetailerDepositContribution'], item['OnTheRoadPrice'])
                yield item

