from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
import urllib
from datetime import datetime, timedelta
import re
import time

class AlfaRomeoSpider(BaseSpider):
    name = 'alfaromeo.co.uk'
    allowed_domains = []
    start_url = ['https://www.alfaromeo.co.uk/promotions', 'https://www.alfaromeo.co.uk/promotions-business']

    def __init__(self):
        super(AlfaRomeoSpider, self).__init__()
    
    def start_requests(self):
        for url in self.start_url:
            if "promotions-business" in url:
                yield Request(url, callback=self.parse_pch_car_url, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_pcp_car_url, headers=self.headers)

    def parse_pcp_car_url(self, response): ### PCP
        url_path = response.xpath('//div[@class="promo-box"]/div[@class="promo-model"]')
        for href in url_path:
            url = self.getText(href, './a/@href')
            href = response.urljoin(url)
            if "/motability" not in href:
                yield Request(href, dont_filter=True, callback=self.pcp_car_inner_link, headers=self.headers)

    def parse_pch_car_url(self, response): ### BUSINESS CONTRACT HIRE
        url_path = response.xpath('//div[@class="promo-box"]/div[@class="promo-model"]')
        for href in url_path:
            url = self.getText(href, './a/@href')
            href = response.urljoin(url)
            # print("url", response.url)
            # print("href", href)
            # input("stop")
            # yield Request(href, dont_filter=True, callback=self.parse_pch_car_list, headers=self.headers)

    def pcp_car_inner_link(self, response): ### PCP
        url_path = response.xpath('//div[@class="detail-promo-list"]/div[@class="detail-promo"]')
        if url_path:
            for href in url_path:
                url = self.getText(href, './a/@href')
                href = response.urljoin(url)
                # print("url", response.url)
                # print("href", href)
                # input("stop")
                yield Request(href, dont_filter=True, callback=self.parse_pcp_car_list, headers=self.headers)
        else:
            yield Request(response.url, dont_filter=True, callback=self.parse_pcp_car_list, headers=self.headers)        


    def parse_pch_car_list(self, response): ### BUSINESS CONTRACT HIRE
        """
        BCH OFFERS
        """

        # CustomerDeposit = response.xpath("//div/[contains(text(), 'Initial rental')]/following-sibling::node()/descendant-or-self::text()").extract()

        # print("url", response.url)
        # print("CustomerDeposit: ", CustomerDeposit)
        # # print("MonthlyPayment: ", MonthlyPayment)
        # # print("DurationofAgreement: ", DurationofAgreement)
        # # print("AverageMilesPerYear: ", AverageMilesPerYear)
        # input("stop")



        # item = CarItem()
        # item['CarMake'] = 'Alfa Romeo'
        # if len(modelname) > 0:
        #     item['CarModel'] = modelname[i]
        # else:
        #     item['CarModel'] = 'N/A'
        # item['TypeofFinance'] = 'Personal Contract Hire'
        # item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
        # item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit[i])
        # item['RetailerDepositContribution'] = 'N/A'
        # item['OnTheRoadPrice'] = 'N/A'
        # item['OptionalPurchase_FinalPayment'] = 'N/A'
        # item['AmountofCredit'] = 'N/A'
        # item['RetailCashPrice'] = 'N/A'
        # item['DurationofAgreement'] = DurationofAgreement[i].split("months")[0]
        # item['TotalAmountPayable'] = 'N/A'
        # item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        # item['RepresentativeAPR'] = 'N/A'
        # item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        # item['ExcessMilageCharge'] = 'N/A'
        # if AverageMilesPerYear:
        #     item['AverageMilesPerYear'] = AverageMilesPerYear[i]
        # else:
        #     item['AverageMilesPerYear'] = 'N/A'
        # # item['OfferExpiryDate'] = OfferExpiryDate
        # item['OfferExpiryDate'] = '31/03/2020'
        # item['DebugMode'] = self.Debug_Mode
        # item['CarimageURL'] = carImg
        # item['WebpageURL'] = response.url
        # try:
        #     item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        #     item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        # except:
        #     item['FinalPaymentPercent'] = 0
        #     item['DepositPercent'] = 0
        # if item['CarModel'] != 'N/A':
        #     yield item



    def parse_pcp_car_list(self, response): ### PCP
        """
        PCP OFFERS
        """


        expDate = self.getTextAll(response, '//div[@data-p2c-cps="LegalNotes"]/p/text()')
        if not expDate:
            expDate = self.getTextAll(response, '//div[@data-p2c-cps="LegalNotes"]/p/span/span/text()')
        if not expDate:
            expDate = self.getTextAll(response, '//div[@data-p2c-cps="LegalNotes"]/p/span/text()')



        regex = r'(31st|30th|29th|28th) ([Jj]an(uary)?|[Ff]eb(ruary)?|[Mm]ar(ch)?|[Aa]pr(il)?|[Mm]ay|[Jj]une?|[Jj]uly?|[Aa]ug(ust)?|[Ss]ept?(ember)?|[Oo]ct(ober)?|[Nn]ov(ember)?|[Dd]ec(ember)?) (\d{4})?|(\b\d{1,2}\/[\d]{1,2}\/\d{2,4})|(\d{2}-[\d]+-\d{2,4})'
        resultSearch = re.findall(regex, expDate)[1]
        expirydate = [x.strip() for x in resultSearch if x.strip()][0]
        OfferExpiryDate = datetime.strptime(expirydate, "%d/%m/%y").strftime('%d/%m/%Y')
        # print("OfferExpiryDate: ", expDate)
        # print("ProductCodes: ", OfferExpiryDate)
        # print("res: ", response.url)
        # input("stop")


        carImg = self.getText(response, '//div[@class="cpspromorangedetailcanvas section"]/section/div/@data-src-medium')

        if "pcp" in response.url:
            divpath = response.xpath('//div[@class="cpspromorangedetailvlinfo section"]//div[@class="dotazioni ffamily"]')
            for data in divpath:
                CarModel = self.getText(data, './/div[contains(text(), "Model")]/following-sibling::div/strong/text()')
                if not CarModel:
                    CarModel = self.getText(data, './/div[@class="card-header"]/div[contains(@class, "span-cont")]/text()')
                OnTheRoadPrice = self.getText(data, './/div[contains(text(), "On the Road Price")]/following-sibling::div/text()')
                RetailerDepositContribution = self.getText(data, './/div[contains(text(), "Alfa Romeo Deposit Contribution")]/following-sibling::div/text()')
                CustomerDeposit = self.getText(data, './/div[contains(text(), "Customer Deposit")]/following-sibling::div/text()')
                AmountofCredit = self.getText(data, './/div[contains(text(), "Amount of Credit")]/following-sibling::div/text()')
                MonthlyPayment = self.getText(data, './/div[contains(text(), "Monthly Payment") or contains(text(), "Monthly Rental")]/following-sibling::div/text()')
                OptionalPurchase_FinalPayment = self.getText(data, './/div[contains(text(), "Optional Final Payment")]/following-sibling::div/text()')
                TotalAmountPayable = self.getText(data, './/div[contains(text(), "Total Amount Payable")]/following-sibling::div/text()')
                AmountofCredit = self.getText(data, './/div[contains(text(), "Amount of Credit")]/following-sibling::div/text()')
                DurationofAgreement = self.getText(data, './/div[contains(text(), "Duration of Contract") or contains(text(), "Duration of Contract")]/following-sibling::div/text()')
                FixedInterestRate_RateofinterestPA = self.getText(data, './/div[contains(text(), "Rate of Interest (Fixed)")]/following-sibling::div/text()')
                RepresentativeAPR = self.getText(data, './/div[contains(text(), "APR")]/following-sibling::div/text()')
                AverageMilesPerYear = self.getText(data, './/div[contains(text(), "Annual Mileage")]/following-sibling::div/text()')
                ExcessMilageCharge = self.getText(data, './/div[contains(text(), "Excess Mileage Charge")]/following-sibling::div/text()')


                item = CarItem()
                item['CarMake'] = 'Alfa Romeo'
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                item['TypeofFinance'] = self.get_type_of_finance('PCP')
                item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                if RetailerDepositContribution:
                    item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
                else:
                    item['RetailerDepositContribution'] = 'N/A'

                item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)

                if OptionalPurchase_FinalPayment:
                    item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment)
                else:
                    item['OptionalPurchase_FinalPayment'] = 'N/A'
                item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
                item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
                if "Months" in DurationofAgreement:
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                elif DurationofAgreement:
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                else:
                    item['DurationofAgreement'] = 'N/A'

                item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)

                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                if RepresentativeAPR:
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                else:
                    item['RepresentativeAPR'] = 'N/A'

                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                if ExcessMilageCharge:
                    item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                else:
                    item['ExcessMilageCharge'] = 'N/A'
                if AverageMilesPerYear:
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
                else:
                    item['AverageMilesPerYear'] = '10000'
                item['OfferExpiryDate'] = OfferExpiryDate
                # item['OfferExpiryDate'] = '31/03/2021'
                item['DebugMode'] = self.Debug_Mode
                item['CarimageURL'] = carImg
                item['WebpageURL'] = response.url
                try:
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['FinalPaymentPercent'] = 0
                    item['DepositPercent'] = 0
                yield item


        elif "pch" in response.url:
            divpath = response.xpath('//div[@class="cpspromorangedetailvlinfo section"]//div[@class="dotazioni ffamily"]')
            for data in divpath:
                CarModel = self.getText(data, './/div[contains(text(), "Model")]/following-sibling::div/strong/text()')
                if not CarModel:
                    CarModel = self.getText(data, './/div[@class="card-header"]/div[contains(@class, "span-cont")]/text()')
                CustomerDeposit = self.getText(data, './/div[contains(text(), "Initial Rental")]/following-sibling::div/text()')
                DurationofAgreement = self.getText(data, './/div[contains(text(), "Duration of Contract")]/following-sibling::div/text()')
                MonthlyPayment = self.getText(data, './/div[contains(text(), "Monthly Rentals") or contains(text(), "Monthly Renewals") or contains(text(), "Monthly Rental")]/following-sibling::div/text()')
                AverageMilesPerYear = self.getText(data, './/div[contains(text(), "Annual Mileage")]/following-sibling::div/text()')


                item = CarItem()
                item['CarMake'] = 'Alfa Romeo'
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                item['TypeofFinance'] = self.get_type_of_finance('PCH')
                item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                item['RetailerDepositContribution'] = 'N/A'
                item['OnTheRoadPrice'] = 'N/A'
                item['OptionalPurchase_FinalPayment'] = 'N/A'
                item['AmountofCredit'] = 'N/A'
                item['RetailCashPrice'] = 'N/A'
                if DurationofAgreement:
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                else:
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)

                item['TotalAmountPayable'] = 'N/A'
                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                item['RepresentativeAPR'] = 'N/A'
                item['FixedInterestRate_RateofinterestPA'] = 'N/A'
                item['ExcessMilageCharge'] = 'N/A'

                if AverageMilesPerYear:
                    item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
                else:
                    item['AverageMilesPerYear'] = 'N/A'
                item['OfferExpiryDate'] = OfferExpiryDate
                # item['OfferExpiryDate'] = '31/03/2021'
                item['DebugMode'] = self.Debug_Mode
                item['CarimageURL'] = carImg
                item['WebpageURL'] = response.url
                try:
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['FinalPaymentPercent'] = 0
                    item['DepositPercent'] = 0
                yield item

        elif "-hp" in response.url:
            divpath = response.xpath('//div[@class="cpspromorangedetailvlinfo section"]//div[@class="dotazioni ffamily"]')
            for data in divpath:
                CarModel = self.getText(data, './/div[contains(text(), "Model")]/following-sibling::div/strong/text()')
                if not CarModel:
                    CarModel = self.getText(data, './/div[@class="card-header"]/div[contains(@class, "span-cont")]/text()')
                OnTheRoadPrice = self.getText(data, './/div[contains(text(), "On the Road Price")]/following-sibling::div/text()')
                RetailerDepositContribution = self.getText(data, './/div[contains(text(), "Alfa Romeo Deposit Contribution")]/following-sibling::div/text()')
                CustomerDeposit = self.getText(data, './/div[contains(text(), "Customer Deposit")]/following-sibling::div/text()')
                MonthlyPayment = self.getText(data, './/div[contains(text(), "Monthly Payment") or contains(text(), "Monthly Rental")]/following-sibling::div/text()')
                TotalAmountPayable = self.getText(data, './/div[contains(text(), "Total Amount Payable")]/following-sibling::div/text()')
                AmountofCredit = self.getText(data, './/div[contains(text(), "Amount of Credit")]/following-sibling::div/text()')
                DurationofAgreement = self.getText(data, './/div[contains(text(), "Duration of Contract") or contains(text(), "Duration of Contract")]/following-sibling::div/text()')
                FixedInterestRate_RateofinterestPA = self.getText(data, './/div[contains(text(), "Rate of Interest (Fixed)")]/following-sibling::div/text()')
                RepresentativeAPR = self.getText(data, './/div[contains(text(), "APR")]/following-sibling::div/text()')
                


                item = CarItem()
                item['CarMake'] = 'Alfa Romeo'
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                item['TypeofFinance'] = self.get_type_of_finance('Hire Purchase')
                item['MonthlyPayment'] = self.make_two_digit_no(MonthlyPayment)
                item['CustomerDeposit'] = self.make_two_digit_no(CustomerDeposit)
                if RetailerDepositContribution:
                    item['RetailerDepositContribution'] = self.remove_gbp(RetailerDepositContribution)
                else:
                    item['RetailerDepositContribution'] = 'N/A'

                item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)

                item['OptionalPurchase_FinalPayment'] = 'N/A'
                item['AmountofCredit'] = self.remove_gbp(AmountofCredit)
                item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
                if "Months" in DurationofAgreement:
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                elif DurationofAgreement:
                    item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
                else:
                    item['DurationofAgreement'] = 'N/A'

                item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)

                item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
                if RepresentativeAPR:
                    item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
                else:
                    item['RepresentativeAPR'] = 'N/A'

                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                item['ExcessMilageCharge'] = 'N/A'
                item['AverageMilesPerYear'] = 'N/A'
                item['OfferExpiryDate'] = OfferExpiryDate
                # item['OfferExpiryDate'] = '31/03/2021'
                item['DebugMode'] = self.Debug_Mode
                item['CarimageURL'] = carImg
                item['WebpageURL'] = response.url
                try:
                    item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['FinalPaymentPercent'] = 0
                    item['DepositPercent'] = 0
                yield item