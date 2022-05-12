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


class PeugeotSpider(BaseSpider):
    name = "peugeot.co.uk"

    allowed_domains = ['peugeot.co.uk', 'offers.peugeot.co.uk']
    # https://offers.peugeot.co.uk/peugeot-offers-page
    start_url = ['https://offers.peugeot.co.uk/available-now', 'https://business.peugeot.co.uk/tools-and-finance/business-ways-to-buy/contract-hire-vans', 'https://offers.peugeot.co.uk/choose-your-peugeot', 'https://offers.peugeot.co.uk/peugeot-offers-page']
    def __init__(self):
        super(PeugeotSpider, self).__init__()

    # def start_requests(self):
        # yield Request(self.start_url, callback=self.parse_model_url, headers=self.headers)
    def start_requests(self):
        for url in self.start_url:
            if "contract-hire-vans" in url:
                yield Request(url, callback=self.parse_contract_hire_vans_url, headers=self.headers)
            elif "/choose-your-peugeot" in url:
                yield Request(url, callback=self.parse_choose_your_peugeot_url, headers=self.headers)
            elif "peugeot-offers-page" in url:
                yield Request(url, callback=self.parse_more_urls, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_more_urls, headers=self.headers)

    def parse_choose_your_peugeot_url(self, response):
        urls =  response.xpath('//ul[@class="offer-list"]/li[@class="col-third"]')
        for a in urls:
            href = self.getText(a, './/a[contains(text(), "Configure It")]/@href')
            url = response.urljoin(href)
            yield Request(url, callback=self.parse__configure_models, headers=self.headers, dont_filter=True,)

    def parse__configure_models(self, response):
        urls =  response.xpath('//div[@id="versions"]//div[@class="col-half box"]')
        for a in urls:
            href = self.getText(a, './/a[contains(text(), "CONFIGURE IT")]/@href')
            url = response.urljoin(href)
            # print("resp: ", response.url)
            # print("url", url)
            # input("stop")
            yield Request(url, callback=self.parse__configure_data, headers=self.headers, dont_filter=True,)

    def parse__configure_data(self, response):
        """CONFIGURATION DATA
        """

        CarimageURL = self.getText(response, '//div[@id="personalise__vizualisation"]/img/@src')
        carModel = self.getText(response, '//div[@class="summary-subtitle"]/h2/text()')
        MonthlyPayment = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Monthly Payments")]/following-sibling::span/text()')
        CustomerDeposit = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Customer Cash Deposit")]/following-sibling::span/text()')
        RetailerDepositContribution = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Deposit Contribution")]/following-sibling::span/text()')
        OnTheRoadPrice = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Vehicle Price (OTR)")]/following-sibling::span/text()')
        AmountofCredit = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Total Amount of Credit")]/following-sibling::span/text()')
        OptionalPurchase_FinalPayment = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Optional Final Payment")]/following-sibling::span/text()')
        DurationofAgreement = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Term Of Agreement")]/following-sibling::span/text()')
        TotalAmountPayable = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Total Amount Payable")]/following-sibling::span/text()')
        RepresentativeAPR = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "APR Representative")]/following-sibling::span/text()')
        FixedInterestRate_RateofinterestPA = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Fixed rate of interest")]/following-sibling::span/text()')
        ExcessMilageCharge = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Excess Mileage Charge")]/following-sibling::span/text()')
        AverageMilesPerYear = self.getText(response, '//div[@id="Widget-FinanceSummary"]//ul/li/span[contains(text(), "Mileage Per Annum")]/following-sibling::span/text()')

        # if "ur-peugeot/configure-all-new-50" in response.url:
        # print("resp: ", response.url)
        # print("carModel", carModel)
        # input("stop")
        if MonthlyPayment:

            item = CarItem()
            item['CarMake'] = 'Peugeot'
            item['CarModel'] = self.remove_special_char_on_excel(carModel)
            item['TypeofFinance'] = self.get_type_of_finance('PCP')
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
            item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
            item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
            item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
            item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
            item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
            item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
            item['TotalAmountPayable'] =  self.remove_gbp(OnTheRoadPrice)
            item['OptionToPurchase_PurchaseActivationFee'] = ''
            item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
            item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
            item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
            item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
            item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
            item['OfferExpiryDate'] = '04/04/2022'
            item['DebugMode'] = self.Debug_Mode
            item['CarimageURL'] = CarimageURL
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            item['WebpageURL'] = response.url
            if item['MonthlyPayment'] != '':
                yield item
            ############################
            ######################### CONFIGURATOR DATA END
            ##########################
    def parse_more_urls(self, response):

        # url = response.xpath('//section[@class="jaf-info-column-block no-margin-top"]//ul[@class="flex-row column-block-list"]/li//a[contains(text(), "View Representative Example")]/@href').extract()

        url = response.xpath('//section[@class="jaf-info-column-block no-margin-top"]//ul[@class="flex-row column-block-list"]/li')
        for a in url:
            urls = self.getText(a, './/a[contains(text(), "View Representative Example")]/@href')
            color = self.getText(a, './/table/tbody/tr/td//span[1]//span[contains(@style, "12pt")]/text()')
            model1 = self.getTexts(a, './/td//span/span/strong//text()')
            if model1:
                model1 = model1[0]
            model2 = self.getTexts(a, './/td//span/span/strong//text()')
            if model2:
                model2 = model2[1]
            carModel = model1 + model2
            # print("carmodel", carModel)
            # input("stop")
            # href = response.urljoin(href)
            # if "?versionId" in href:
            #     if len(href) == 204:
            #         urls = href
            #     elif len(href) == 233:
            #         urls = href.split("offers.peugeot.co.uk/ ")[1]
            if urls:
                versionId = urls.split("versionId=")[1].split("&")[0]
                exteriorColor = urls.split("colourExt=")[1].split("&")[0]
                interiorColor = urls.split("colourInt=")[1].split("&")[0]
                duration = urls.split("duration=")[1].split("&")[0]
                productKey = urls.split("productCode=")[1].split("&")[0]
                mileage = urls.split("mileage=")[1].split("&")[0]
                deposit = urls.split("deposit=")[1].split("&")[0]
                link = 'https://offers.peugeot.co.uk/preconfigured-car?versionId='+versionId+'&colourExt='+exteriorColor+'&colourInt='+interiorColor+'&productCode='+productKey+'&duration='+duration+'&mileage='+mileage+'&deposit='+deposit+'&representative=true&targetPageCode=G06'
                financeOverlayUrl = "https://offers.peugeot.co.uk/financeOverlayRepresentative"
                formdata = {
                    'versionId':versionId,
                    'duration':duration,
                    'exteriorColor':exteriorColor,
                    'interiorColor':interiorColor,
                    'productKey':productKey,
                    'mileage':mileage,
                    'deposit':deposit
                }
                yield FormRequest(financeOverlayUrl, formdata=formdata, callback=self.parse_model, headers=self.headers, dont_filter=True, meta={"link":link, "color":color, "carModel":carModel})

    def parse_model(self, response):
        """PCP cars data
        """

        weblink = response.meta['link']
        carColor = response.meta['color']

        carModel = self.getText(response, '//h3[@class="popup-view-example-subheader"]/text()')
        if carModel == '':
            carModel = response.meta['carModel']
        MonthlyPayment = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Monthly Payments")]/following-sibling::span/text()')
        CustomerDeposit = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Customer Cash Deposit")]/following-sibling::span/text()')
        RetailerDepositContribution = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Peugeot Deposit Contribution")]/following-sibling::span/text()')
        OnTheRoadPrice = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Vehicle Price (OTR)")]/following-sibling::span/text()')
        OptionalPurchase_FinalPayment = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Optional Final Payment")]/following-sibling::span/text()')
        AmountofCredit = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Total Charge For Credit")]/following-sibling::span/text()')
        DurationofAgreement = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Term Of Agreement")]/following-sibling::span/text()')
        TotalAmountPayable = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Total Amount Payable")]/following-sibling::span/text()')
        RepresentativeAPR = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "APR Representative")]/following-sibling::span/text()')
        FixedInterestRate_RateofinterestPA = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Fixed rate of interest")]/following-sibling::span/text()')
        ExcessMilageCharge = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Excess Mileage Charge")]/following-sibling::span/text()')
        AverageMilesPerYear = self.getText(response, '//ul[@class="popup-view-example-list"]/li/span[contains(text(), "Mileage Per Annum")]/following-sibling::span/text()')

        offer_exp = self.getTextAll(response, '//div[@id="view-rep-example-text"]//p/span/span/span/text()')
        offerExp = offer_exp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "")
        OfferExpiryDate = self.dateMatcher(offerExp)[1]

        # print("url", response.url)
        # # print("OfferExpiryDate", OfferExpiryDate)
        # # print("CustomerDeposit", CustomerDeposit)
        # input("stop")

        item = CarItem()
        item['CarMake'] = 'Peugeot'
        # item['CarModel'] = carModel +' '+ carColor ### With Color
        item['CarModel'] = self.remove_special_char_on_excel(carModel)
        item['TypeofFinance'] = self.get_type_of_finance('PCP')
        item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
        item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
        if item['CustomerDeposit']:
            item['CustomerDeposit'] = float(item['CustomerDeposit'])
        item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
        if item['RetailerDepositContribution']:
            item['RetailerDepositContribution'] = float(item['RetailerDepositContribution'])
        item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
        if item['OnTheRoadPrice']:
            item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
        item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
        item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
        ExcessMilageCharge = self.remove_gbp(ExcessMilageCharge)
        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
        item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
        item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
        # item['OfferExpiryDate'] = '31/03/2021'
        item['OfferExpiryDate'] = OfferExpiryDate
        item['DebugMode'] = self.Debug_Mode
        item['CarimageURL'] = ''
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        item['WebpageURL'] = weblink
        if item['MonthlyPayment'] != '':
            yield item

    def parse_contract_hire_vans_url(self, response):
        """
        CH VANS OFFER getting iTEMS
        """

        other_data_path = self.getText(response, '//div[@class="small-12 columns"]/p/span[contains(text(), "Contract Hire prices")]/text()')
        if other_data_path:
            DurationofAgreement = other_data_path.split("are based on a")[1].split("-month contract")[0]
        else:
            DurationofAgreement = 'N/A'

        ### OFFER Expiry ###
        # offer_exp = self.getTextAll(response, '//div[@class="small-12 columns"]//p/text()')
        # print("offer_exp", offer_exp)
        # print("res", response.url)
        # input("stop")

        # OfferExpiryDate = offer_exp.split("registered between")[1].split("unless withdrawn")[0]
        ### OFFER Expiry ###


        div_path = response.xpath("//div[@id='ndp-pc12-3-colonnes_150_5']/article[@class='medium-4 columns']")
        for div in div_path:
            price = self.getText(div, './/h2[@class="text-left"]/text()')
            regex = r"[\$|€|£\20AC\00A3]{1}\d+\.?\d{0,2}"
            MonthlyPayment = self.remove_gbp(re.search(regex, price).group())
            CarimageURL = self.getText(div, './figure//picture/source/@data-srcset')

            peugoet_Model = self.getText(div, './/p/strong/span/text()')
            if not peugoet_Model:
                peugoet_Model = self.getText(div, './/p/span/strong/text()')

            item = CarItem()
            item['CarMake'] = 'Peugeot'
            item['CarModel'] = self.remove_special_char_on_excel(peugoet_Model)
            item['TypeofFinance'] = self.get_type_of_finance('Commercial Contract Hire')
            item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
            item['CustomerDeposit'] = 'N/A'
            item['RetailerDepositContribution'] = ''
            item['OnTheRoadPrice'] = ''
            item['OptionalPurchase_FinalPayment'] = ''
            item['AmountofCredit'] = ''
            item['DurationofAgreement'] = DurationofAgreement
            item['TotalAmountPayable'] = ''
            item['OptionToPurchase_PurchaseActivationFee'] = ''
            item['RepresentativeAPR'] = ''
            item['FixedInterestRate_RateofinterestPA'] = ''
            item['ExcessMilageCharge'] = ''
            item['AverageMilesPerYear'] = '6000'
            item['RetailCashPrice'] = ''
            # item['OfferExpiryDate'] = OfferExpiryDate
            item['OfferExpiryDate'] = '04/04/2022'
            item['DebugMode'] = self.Debug_Mode
            item['CarimageURL'] = CarimageURL
            item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
            try:
                item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
            except:
                item['DepositPercent'] = float()
            item['WebpageURL'] = response.url
            if item['MonthlyPayment'] != '':
                yield item
