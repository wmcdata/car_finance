# -*- coding: utf-8 -*-
from scrapy import Selector
from scrapy.http import Request, FormRequest, HtmlResponse
from car_finance_scrapy.items import *
from car_finance_scrapy.spiders.base.base_spider import BaseSpider
# from scrapy.conf import settings
import urllib
from datetime import datetime, timedelta, date
import re
import time
import json
from scrapy.selector import Selector
import requests
# 'https://store.vauxhall.co.uk/fc/api/v3/6/en/calculate-for-summary'

# https://www.vauxhall.co.uk/offers-finance/car-offers.html  Car offers
# https://www.vauxhall.co.uk/offers-finance/van-offers.html Vans offers

class VauxhallSpider(BaseSpider):
    name = "vauxhall.co.uk"

    handle_httpstatus_list = [404]

    allowed_domains = ['vauxhall.co.uk']
    """https://store.vauxhall.co.uk/fc/api/v3/6/en/finance-quote"""
    """https://store.vauxhall.co.uk/configurable/"""
    """https://www.vauxhall.co.uk/offers-finance/finance-calculator.html"""


    # https://tools.vauxhall.co.uk/FFC_SPC/seriesData
    # start_url = ['https://store.vauxhall.co.uk/trim/configurable/new-corsa-5-door','https://store.vauxhall.co.uk/trim/configurable/new-corsa-e-5-door','https://store.vauxhall.co.uk/trim/configurable/new-mokka-5-door','https://store.vauxhall.co.uk/trim/configurable/new-mokka-e-5-door','https://store.vauxhall.co.uk/trim/configurable/crossland-5-door','https://store.vauxhall.co.uk/trim/configurable/grandland-x','https://store.vauxhall.co.uk/trim/configurable/grandland-x-hybrid','https://store.vauxhall.co.uk/trim/configurable/astra','https://store.vauxhall.co.uk/trim/configurable/astra-sports-tourer','https://store.vauxhall.co.uk/trim/configurable/insignia','https://store.vauxhall.co.uk/trim/configurable/combo','https://store.vauxhall.co.uk/trim/configurable/new-vivaro-e-life-elite','https://tools.vauxhall.co.uk/static/ffc_cardata.json', 'https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/electric/flexible-pcp/partials/se-nav.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/electric/flexible-pcp/partials/elite-nav.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/electric/flexible-pcp/partials/elite-nav1.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/petrol-diesel/flexible-pcp/partials/se.html','https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/petrol-diesel/flexible-pcp/partials/sri-nav.html','https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/petrol-diesel/flexible-pcp/partials/se.html','https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/petrol-diesel/flexible-pcp/partials/griffin.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/petrol-diesel/flexible-pcp/partials/sri.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/petrol-diesel/flexible-pcp/partials/elite-nav-premium.html','https://www.vauxhall.co.uk/cars/new-crossland/offers-finance/flexible-pcp/partials/griffin.html','https://www.vauxhall.co.uk/cars/new-crossland/offers-finance/flexible-pcp/partials/si-nav.html','https://www.vauxhall.co.uk/cars/new-crossland/offers-finance/flexible-pcp/partials/elite.html', 'https://www.vauxhall.co.uk/offers/van-offers.html', 'https://www.vauxhall.co.uk/offers-finance/business-leasing.html', 'https://www.vauxhall.co.uk/cars/grandland-x/offers-finance/petrol-diesel/flexible-pcp/partials/se.html','https://store.vauxhall.co.uk/trim/configurable/finance/new-corsa-e-5-door?_ga=2.241620865.2030945993.1620020370-46638326.1566990177', 'https://store.vauxhall.co.uk/trim/configurable/finance/grandland-x-hybrid?_ga=2.3591219.2030945993.1620020370-46638326.1566990177', 'https://www.vauxhall.co.uk/vans/new-movano/offers-finance/electric/headline-offers/Partials/conditional-sale-full-example1.html']

    start_url = ['https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/se.html','https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/sri.html', 'https://www.vauxhall.co.uk/cars/insignia/offers-finance/flexible-pcp/partials/design.html', 'https://www.vauxhall.co.uk/cars/insignia/offers-finance/flexible-pcp/partials/gs-line.html','https://www.vauxhall.co.uk/cars/mokka/offers-finance/electric/flexible-pcp/partials/sri-nav.html','https://www.vauxhall.co.uk/cars/mokka/offers-finance/electric/flexible-pcp/partials/ultimate.html', 'https://www.vauxhall.co.uk/cars/mokka/offers-finance/petrol-diesel/flexible-pcp/partials/se.html', 'https://www.vauxhall.co.uk/cars/mokka/offers-finance/petrol-diesel/flexible-pcp/partials/sri-nav.html','https://www.vauxhall.co.uk/cars/mokka/offers-finance/petrol-diesel/flexible-pcp/partials/elite.html','https://www.vauxhall.co.uk/cars/new-astra/offers-finance/sports-tourer/petrol-diesel/flexible-pcp/partials/design.html','https://www.vauxhall.co.uk/cars/new-astra/offers-finance/sports-tourer/petrol-diesel/flexible-pcp/partials/gs-line.html','https://www.vauxhall.co.uk/cars/new-astra/offers-finance/sports-tourer/hybrid-e/flexible-pcp/partials/gs-line.html','https://www.vauxhall.co.uk/cars/crossland/offers-finance/flexible-pcp.html','https://www.vauxhall.co.uk/cars/crossland/offers-finance/flexible-pcp/partials/gs-line.html','https://www.vauxhall.co.uk/cars/crossland/offers-finance/flexible-pcp/partials/ultimate.html', 'https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/elite.html', 'https://store.vauxhall.co.uk/trim/configurable/new-corsa-5-door','https://store.vauxhall.co.uk/trim/configurable/corsa-e-5-door','https://store.vauxhall.co.uk/trim/configurable/corsa-5-door', 'https://store.vauxhall.co.uk/trim/configurable/new-corsa-e-5-door','https://store.vauxhall.co.uk/trim/configurable/new-mokka-5-door','https://store.vauxhall.co.uk/trim/configurable/mokka-e-5-door', 'https://store.vauxhall.co.uk/trim/configurable/mokka-5-door', 'https://store.vauxhall.co.uk/trim/configurable/new-astra-5-door', 'https://store.vauxhall.co.uk/trim/configurable/new-astra-sports-tourer', 'https://store.vauxhall.co.uk/trim/configurable/new-mokka-e-5-door','https://store.vauxhall.co.uk/trim/configurable/crossland-5-door','https://store.vauxhall.co.uk/trim/configurable/new-grandland-plug-in-hybrid', 'https://store.vauxhall.co.uk/trim/configurable/new-grandland', 'https://store.vauxhall.co.uk/trim/configurable/combo-e-life','https://store.vauxhall.co.uk/trim/configurable/vivaro-panel-van', 'https://store.vauxhall.co.uk/trim/configurable/combo-e-panel-van',  'https://store.vauxhall.co.uk/trim/configurable/grandland-x','https://store.vauxhall.co.uk/trim/configurable/grandland-x-hybrid','https://store.vauxhall.co.uk/trim/configurable/astra','https://store.vauxhall.co.uk/trim/configurable/astra-sports-tourer','https://store.vauxhall.co.uk/trim/configurable/insignia','https://store.vauxhall.co.uk/trim/configurable/combo','https://store.vauxhall.co.uk/trim/configurable/new-vivaro-e-life-elite','https://tools.vauxhall.co.uk/static/ffc_cardata.json', "https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/se-nav.html","https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/se.html","https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/sri.html","https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/elite-edition.html","https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/electric/flexible-pcp/partials/se-nav.html","https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/electric/flexible-pcp/partials/sri-nav.htm","https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/electric/flexible-pcp/partials/elite-nav-premium.html","https://www.vauxhall.co.uk/cars/new-astra/offers-finance/hatchback/hybrid/flexible-pcp/partials/gs-line.html","https://www.vauxhall.co.uk/cars/new-astra/offers-finance/hatchback/petrol-diesel/flexible-pcp/partials/ultimate.html","https://www.vauxhall.co.uk/cars/grandland/offers-finance/hybrid/flexible-pcp/partials/elite.html","https://www.vauxhall.co.uk/cars/new-insignia/offers-finance/flexible-pcp/partials/se-edition.html",
    "https://www.vauxhall.co.uk/cars/new-insignia/offers-finance/flexible-pcp/partials/sri-premium.html","https://www.vauxhall.co.uk/cars/grandland/offers-finance/petrol-diesel/flexible-pcp/partials/elite.html","https://www.vauxhall.co.uk/cars/combo-life/offers-finance/electric/flexible-pcp/partials/SE-5.html","https://www.vauxhall.co.uk/cars/combo-life/offers-finance/electric/flexible-pcp/partials/SE-XL-7.html","https://www.vauxhall.co.uk/cars/vivaro-life/offers-finance/electric/flexible-pcp/partials/combi.html","https://www.vauxhall.co.uk/cars/vivaro-life/offers-finance/electric/flexible-pcp/partials/elite.html","https://www.vauxhall.co.uk/cars/new-crossland/offers-finance/flexible-pcp/partials/se.html","https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/electric/flexible-pcp/partials/elite-nav1.html","https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/elite-nav.html","https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/elite-nav1.html",'https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/electric/flexible-pcp/partials/se-nav.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/electric/flexible-pcp/partials/elite-nav.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/electric/flexible-pcp/partials/elite-nav1.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/petrol-diesel/flexible-pcp/partials/se.html','https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/petrol-diesel/flexible-pcp/partials/sri-nav.html','https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/petrol-diesel/flexible-pcp/partials/se.html','https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/petrol-diesel/flexible-pcp/partials/griffin.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/petrol-diesel/flexible-pcp/partials/sri.html','https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/petrol-diesel/flexible-pcp/partials/elite-nav-premium.html','https://www.vauxhall.co.uk/cars/new-crossland/offers-finance/flexible-pcp/partials/griffin.html','https://www.vauxhall.co.uk/cars/new-crossland/offers-finance/flexible-pcp/partials/si-nav.html','https://www.vauxhall.co.uk/cars/new-crossland/offers-finance/flexible-pcp/partials/elite.html', 'https://www.vauxhall.co.uk/offers/van-offers.html', 'https://www.vauxhall.co.uk/offers-finance/business-leasing.html', 'https://www.vauxhall.co.uk/cars/grandland-x/offers-finance/petrol-diesel/flexible-pcp/partials/se.html', 'https://store.vauxhall.co.uk/trim/configurable/finance/new-corsa-e-5-door?_ga=2.241620865.2030945993.1620020370-46638326.1566990177', 'https://store.vauxhall.co.uk/trim/configurable/finance/grandland-x-hybrid?_ga=2.3591219.2030945993.1620020370-46638326.1566990177', 'https://www.vauxhall.co.uk/vans/movano/offers-finance/headline-offers/Partials/conditional-sale-full-example1.html', 'https://www.vauxhall.co.uk/vans/new-movano/offers-finance/diesel/headline-offers/Partials/conditional-sale-full-example1.html', "https://www.vauxhall.co.uk/vans/new-movano/offers-finance/electric/headline-offers/Partials/conditional-sale-full-example1.html", "https://www.vauxhall.co.uk/vans/vivaro/offers-finance/electric/0-per-cent-conditional-sale/partials/conditional-sale-full-example.html", "https://www.vauxhall.co.uk/vans/combo/offers-finance/electric/headline-offers/Partials/conditional-sale-full-example.html", "https://www.vauxhall.co.uk/vans/combo/offers-finance/petrol-diesel/headline-offers/Partials/conditional-sale-full-example.html", "https://www.vauxhall.co.uk/vans/vivaro/offers-finance/diesel/headline-offers/Partials/conditional-sale-full-example.html"
    "https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/gs-line.html", 'https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/ultimate.html', 'https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/design.html', 'https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/gs-line.html', 'https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/ultimate.html', 'https://www.vauxhall.co.uk/cars/mokka/offers-finance/petrol-diesel/flexible-pcp/partials/design.html', 'https://www.vauxhall.co.uk/cars/mokka/offers-finance/petrol-diesel/flexible-pcp/partials/gs-line.html', 'https://www.vauxhall.co.uk/cars/mokka/offers-finance/petrol-diesel/flexible-pcp/partials/ultimate.html', 'https://www.vauxhall.co.uk/cars/crossland/offers-finance/flexible-pcp/partials/design.html', 'https://www.vauxhall.co.uk/cars/new-astra/offers-finance/hatchback/hybrid/flexible-pcp/partials/ultimate.html', 'https://www.vauxhall.co.uk/cars/new-astra/offers-finance/hatchback/petrol-diesel/flexible-pcp/partials/design.html', 'https://www.vauxhall.co.uk/cars/new-astra/offers-finance/hatchback/petrol-diesel/flexible-pcp/partials/gs-line.html', 'https://www.vauxhall.co.uk/cars/grandland/offers-finance/hybrid/flexible-pcp/partials/gs-line.html', 'https://www.vauxhall.co.uk/cars/grandland/offers-finance/hybrid/flexible-pcp/partials/ultimate.html', 'https://www.vauxhall.co.uk/cars/grandland/offers-finance/petrol-diesel/flexible-pcp/partials/design.html', 'https://www.vauxhall.co.uk/cars/grandland/offers-finance/petrol-diesel/flexible-pcp/partials/gs-line.html', 'https://www.vauxhall.co.uk/cars/grandland/offers-finance/petrol-diesel/flexible-pcp/partials/ultimate.html', 'https://www.vauxhall.co.uk/cars/mokka/offers-finance/electric/flexible-pcp/partials/gs-line.html', 
    ]


# "https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/se-nav.html",
# "https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/se.html",
# "https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/sri.html",
# "https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/elite-edition.html",
# "https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/elite-nav.html",
# "https://www.vauxhall.co.uk/cars/corsa/offers-finance/electric/flexible-pcp/partials/elite-nav1.html",

# "https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/electric/flexible-pcp/partials/se-nav.html",
# "https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/electric/flexible-pcp/partials/sri-nav.htm",
# "https://www.vauxhall.co.uk/cars/new-mokka/offers-finance/electric/flexible-pcp/partials/elite-nav-premium.html",

# "https://www.vauxhall.co.uk/cars/new-astra/offers-finance/hatchback/hybrid/flexible-pcp/partials/gs-line.html",
# "https://www.vauxhall.co.uk/cars/new-astra/offers-finance/hatchback/petrol-diesel/flexible-pcp/partials/ultimate.html",

# "https://www.vauxhall.co.uk/cars/new-corsa/offers-finance/electric/flexible-pcp/partials/elite-nav1.html",

# "https://www.vauxhall.co.uk/cars/new-insignia/offers-finance/flexible-pcp/partials/se-edition.html",
# "https://www.vauxhall.co.uk/cars/new-insignia/offers-finance/flexible-pcp/partials/sri-premium.html",

# "https://www.vauxhall.co.uk/cars/grandland/offers-finance/hybrid/flexible-pcp/partials/elite.html",
# "https://www.vauxhall.co.uk/cars/grandland/offers-finance/petrol-diesel/flexible-pcp/partials/elite.html",

# "https://www.vauxhall.co.uk/cars/combo-life/offers-finance/electric/flexible-pcp/partials/SE-5.html",
# "https://www.vauxhall.co.uk/cars/combo-life/offers-finance/electric/flexible-pcp/partials/SE-XL-7.html",


# "https://www.vauxhall.co.uk/cars/vivaro-life/offers-finance/electric/flexible-pcp/partials/combi.html",
# "https://www.vauxhall.co.uk/cars/vivaro-life/offers-finance/electric/flexible-pcp/partials/elite.html",

# "https://www.vauxhall.co.uk/cars/new-crossland/offers-finance/flexible-pcp/partials/se.html",



    def __init__(self):
        super(VauxhallSpider, self).__init__()

    # def start_requests(self):

    def start_requests(self):
        for url in self.start_url:
            # if "ffc_cardata.json" in url:
            #     yield Request(url, callback=self.parse_model, headers=self.headers)

            if "cars/new-crossland/offers-finance" in url or "cars/new-corsa/offers-finance" in url or "/cars/corsa/offers-finance" in url or "cars/grandland-x/offers-finance" in url or "cars/new-mokka/offers-finance/" in url or "/vans/new-movano/offers-finance" in url or "vans/new-movano/offers-finance/diesel/" in url or "/vans/new-movano/offers-finance/electric" in url or "vans/vivaro/offers-finance/" in url or "vans/combo/offers-finance/electric" in url or "vans/combo/offers-finance/petrol-diesel/" in url or "/cars/new-astra/offers-finance" in url or "/cars/new-insignia/offers-finance" in url or "cars/grandland/offers-finance" in url or "/cars/combo-life/offers-finance" in url or "/cars/vivaro-life/offers-finance" in url or "/cars/insignia/offers-finance" in url or "/cars/mokka/offers-finance" in url or "/cars/crossland/offers-finance" in url or "/offers-finance/" in url:
            # if "https://www.vauxhall.co.uk/cars/corsa/offers-finance/petrol-diesel/flexible-pcp/partials/se.html" in url:    
                yield Request(url, callback=self.parse_electric_model, headers=self.headers, dont_filter=True)
            elif "petrol-diesel/flexible-pcp.html" in url: ### PCP
                yield Request(url, callback=self.parse_petrol_desel_link, headers=self.headers)
            elif "business-leasing" in url: ### BCH
                yield Request(url, callback=self.parse_bch_offers_link, headers=self.headers)
            elif "/trim/configurable/finance" in url: ### BCH
                yield Request(url, callback=self.parse_pcp_configurable, headers=self.headers)
            elif "/trim/configurable/" in url: ### PCP
                yield Request(url, callback=self.parse_pcp_Calculated, headers=self.headers)
            else:
                yield Request(url, callback=self.parse_url_links, headers=self.headers)

    def parse_url_links(self, response):
        path = response.xpath('//div[@class="row medium-collapse grid-enable-spacing"]/div[@class="small-12 medium-4 columns"]')
        for url in path:
           imageURL = self.getText(url, './/picture//img/@srcset')
           CarimageURL = response.urljoin(imageURL)
           href = self.getText(url, './a/@href')
           href = response.urljoin(href)
           yield Request(href, callback=self.parse_specific_vans, headers=self.headers, meta={"CarimageURL":CarimageURL})


    def parse_petrol_desel_link(self, response):
        """PETROL DESEL PCP
        """
        path = self.getTexts(response, '//a[contains(text(), "See representative example") or contains(text(), "See example")]/@href')
        for url in path:
            href = response.urljoin(url)
            # print("url", response.url)
            # print("href", href)
            # input("stop")
            yield Request(href, callback=self.parse_electric_model, headers=self.headers)

    def parse_pcp_Calculated(self, response):
        """Calculated data
        """
        json_string = self.getText(response, '//script[@id="__NEXT_DATA__"]/text()')
        JO = json.loads(json_string)
        trims = JO['props']['initialState']['TrimSelector']['configurable']['trims']

        for trim in trims:

            id = trim['_id']
            lcdv16Code = id.split("+")[0].replace(" ", "")

            options_code_2 = id.split("+")[1]
            options_code_1 = id.split("+")[2]
            prices_object = trim['_properties']['object']['prices']
            Model_name = trim['_properties']['object']['nameplate']['description']
            Model_name_varient = trim['_properties']['object']['specPack']['title']
            Model_name_id = trim['_properties']['object']['nameplate']['id']
            required_prices = [(i) for i in prices_object if i['type']=="Employee"]
            basicPriceInclTax = required_prices[0]['inputPriceInclTax']
            complete_model_name = Model_name +" "+ Model_name_varient
            engine_specification_object = trim['_properties']['object']['engine']['specs']
            fiscalProperties_co2Emissions_object = [(i) for i in engine_specification_object if i['label']=="CO2 combined (g/km)"][0]
            fiscalProperties_co2Emissions_value = fiscalProperties_co2Emissions_object['value']
            extraFields_object = trim['_properties']['object']['extraFields']['pricesV2'][1]
            registrationFee = extraFields_object['breakdown']['registrationFee']
            delivery = extraFields_object['breakdown']['deliveryInclTax']
            roadFundLicence = extraFields_object['breakdown']['vehicleExciseDuty']
            # productKey =  trim['_properties']['object']['financeProducts'][0]['key']

            annualMileage = 10000
            # if "CORSA" in complete_model_name.upper():
            deposit = 20

            durations = [36,42,48]
            for duration in durations:
                url = "https://api.groupe-psa.com/applications/onlinefinance-simulation-offer/v1/financialsimulation/offer/servicelevels/criteriacompatibility"
                payload = '{"context":{"siteCode":"SME","journeyType":"ACVNR","distributionBrand":"OV","countryCode":"GB","languageCode":"en","customer":{"clientType":"P"},"componentCode":"SOW"},"vehicle":{"lcdv16Code":"'+lcdv16Code+'","pricing":{"basicPriceInclTax":'+str(basicPriceInclTax)+',"netPriceInclTax":'+str(basicPriceInclTax)+'},"fiscalProperties":{"co2Emissions":0,"wltpCo2Emissions":0,"registrationFees":55},"otrCosts":{"delivery":{"amountInclTax":740}},"options":[{"code":"'+options_code_1+'","pricing":{"basicPriceInclTax":0,"netPriceInclTax":0}},{"code":"'+options_code_2+'","pricing":{"basicPriceInclTax":0,"netPriceInclTax":0}}]},"parameters":{"deposit":'+str(deposit)+',"duration":'+str(duration)+',"annualMileage":10000,"depositAmountKind":"PCT","productKey":"PCP"}}'


                headers = {
                  'accept': 'application/json',
                  'Accept-Encoding': 'gzip, deflate, br',
                  'Accept-Language': 'en-US,en;q=0.9',
                  'Connection': 'keep-alive',
                  'content-type': 'application/json',
                  'Host': 'api.groupe-psa.com',
                  'Origin': 'https://store.vauxhall.co.uk',
                  'Referer': 'https://store.vauxhall.co.uk/',
                  'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
                  'sec-ch-ua-mobile': '?0',
                  'Sec-Fetch-Dest': 'empty',
                  'Sec-Fetch-Mode': 'cors',
                  'Sec-Fetch-Site': 'cross-site',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                  'x-ibm-client-id': '4b1a1cd8-776f-4309-868d-e74ad4c39d83',
                  'Cookie': 'PSACountry=US'
                }

                yield Request(url, callback=self.parse_items, method="POST", body=payload, headers=headers, meta={"car_model_name":complete_model_name}, dont_filter=True)



    def parse_items(self, response):
        JO = json.loads(response.body)
        # print(JO)
        # input("sto")
        carModel = response.meta['car_model_name']
        packageSelectionObject = JO['packageSelection'][0]
        financingDetailsObject = packageSelectionObject['financingDetails'][0]
        MonthlyPayments = packageSelectionObject['price']
        displayLinesObject = financingDetailsObject['displayLines']
        DurationofAgreement = [(i) for i in displayLinesObject if "Duration of Agreement" in i['label']][0]['value']
        CustomerDeposit = [(i) for i in displayLinesObject if "Customer Deposit" in i['label']][0]
        OnTheRoadPrice = [(i) for i in displayLinesObject if "Vauxhall Store Price/OTR" in i['label']][0]
        OptionalPurchase_FinalPayment = [(i) for i in displayLinesObject if "Optional Final Payment" in i['label']][0]
        AmountofCredit = [(i) for i in displayLinesObject if "Total Amount of Credit" in i['label']][0]
        TotalAmountPayable = [(i) for i in displayLinesObject if "Total Amount Payable" in i['label']][0]
        RepresentativeAPR = [(i) for i in displayLinesObject if "APR Representative" in i['label']][0]
        FixedInterestRate_RateofinterestPA = [(i) for i in displayLinesObject if "Fixed Rate of Interest Per Year (True)" in i['label']][0]
        ExcessMilageCharge = [(i) for i in displayLinesObject if "Mileage Charge (per mile)" in i['label']][0]
        AnnualMileage = [(i) for i in displayLinesObject if "Mileage per annum" in i['label']][0]


        expiry_date = date.today() + timedelta(days=14)
        formated_date_expiry = expiry_date.strftime('%d/%m/%Y')


        item = CarItem()
        item['CarMake'] = 'Vauxhall'
        item['CarModel'] = self.remove_special_char_on_excel(carModel)
        item['TypeofFinance'] = self.get_type_of_finance("PCP")
        item['MonthlyPayment'] = MonthlyPayments
        item['CustomerDeposit'] = self.make_two_digit_no_vauxhall(CustomerDeposit['value'])
        item['RetailerDepositContribution'] = "N/A"
        item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice['value'])
        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(OptionalPurchase_FinalPayment['value'])
        item['AmountofCredit'] = self.remove_gbp(AmountofCredit['value'])
        item['DurationofAgreement'] = DurationofAgreement
        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable['value'])
        item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
        item['RepresentativeAPR'] = RepresentativeAPR['value']
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA['value'])
        item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge['value'])
        item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage['value'])
        item['OfferExpiryDate'] = formated_date_expiry
        item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice['value'])
        item['CarimageURL'] = ''
        item['WebpageURL'] = 'https://store.vauxhall.co.uk/configurable/'
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        yield item


    def parse_pcp_configurable(self, response):
        """PCP Confugure Finance - Corsa e/ Grandland-x-hybrid
        """
        link = response.url
        if "finance/" in link:
            modelTrim = link.split("finance/")[1].split("?")[0]

            url = "https://store.vauxhall.co.uk/spc-api/api/v1/gb/en/OV/car-details-list"

            payload = json.dumps({
            "aggregationParams": {
                "levelAggregations": [
                {
                    "name": "specPack.id",
                    "nesting": [
                    "specPack",
                    "id"
                    ],
                    "children": []
                }
                ],
                "relevancyAggregations": [
                {
                    "name": "prices.monthlyPrices.amount",
                    "fields": [
                    "*"
                    ],
                    "parent": "specPack.id",
                    "operation": {
                    "size": 1,
                    "sort": "asc"
                    }
                },
                {
                    "name": "prices.monthlyPrices.amount",
                    "fields": [
                    "*"
                    ],
                    "parent": "specPack",
                    "operation": {
                    "size": 1,
                    "sort": "asc"
                    }
                }
                ]
            },
            "filters": [
                {
                "nesting": [
                    "nameplateBodyStyleSlug"
                ],
                "name": "nameplateBodyStyleSlug",
                "operator": "EQUALS",
                "value": modelTrim,
                "parent": None
                },
                {
                "nesting": [
                    "prices",
                    "monthlyPrices",
                    "amount"
                ],
                "name": "prices.monthlyPrices.amount.global",
                "operator": "BETWEEN",
                "value": {
                    "from": 1,
                    "to": 99999
                },
                "parent": None
                },
                {
                "nesting": [
                    "stock"
                ],
                "name": "stock",
                "operator": "EQUALS",
                "value": "false"
                }
            ],
            "extra": {
                "journey": "finance"
            }
            })
            headers = {
            'Content-Type': 'application/json'
            }

            responses = requests.request("POST", url, headers=headers, data=payload)
            jsonLoads = json.loads(responses.text)
            items_data = jsonLoads['items'][0]
            allitems = items_data['items']
            for items in allitems:
                modelName = items['items']['prices.monthlyPrices.amount'][0]['model']['title']
                specPack = items['items']['prices.monthlyPrices.amount'][0]['specPack']['title']
                engine = items['items']['prices.monthlyPrices.amount'][0]['engine']['title']
                CarModel = modelName +' '+specPack +' '+ engine

                imageurl = items['items']['prices.monthlyPrices.amount'][0]['exteriorColour']['images'][0]['url']
                externalId = items['items']['prices.monthlyPrices.amount'][0]['externalId']
                url = "https://store.vauxhall.co.uk/fc/api/v3/6/en/calculate-for-summary"

                payload = json.dumps({
                "carConfigId": externalId
                })
                headers = {
                'Content-Type': 'application/json'
                }

                resultResponse = requests.request("POST", url, headers=headers, data=payload)
                resultData = json.loads(resultResponse.text)
                blocks = resultData['blocks'][0]
                Roomdata = dict()
                displayLines = blocks['displayLines']
                for values in displayLines:
                    label = values['label']
                    value = values['value']
                    Roomdata.update({label:value})
                DurationofAgreement = Roomdata['Duration of Agreement']
                TypeofFinance = Roomdata['Finance Product']
                OnTheRoadPrice = Roomdata['Vauxhall Store Price/OTR']
                CustomerDeposit = Roomdata['Customer Deposit']
                AmountofCredit = Roomdata['Total Amount of Credit']
                TotalAmountPayable = Roomdata['Total Amount Payable']
                MonthlyPayment = Roomdata['47 Monthly Payments']
                OptionalPurchase_FinalPayment = Roomdata['Optional Final Payment']
                RepresentativeAPR = Roomdata['APR Representative']
                FixedInterestRate_RateofinterestPA = Roomdata['Fixed Rate of Interest Per Year (True)']
                AverageMilesPerYear = Roomdata['Mileage per annum']
                ExcessMilageCharge = Roomdata['Mileage Charge (per mile)']

                # print(Roomdata)
                # print(CarModel)
                # input()

                item = CarItem()
                item['CarMake'] = 'Vauxhall'
                item['CarModel'] = self.remove_special_char_on_excel(CarModel)
                item['TypeofFinance'] = self.get_type_of_finance(TypeofFinance)
                item['MonthlyPayment'] = MonthlyPayment
                item['CustomerDeposit'] = self.make_two_digit_no_vauxhall(CustomerDeposit)
                item['RetailerDepositContribution'] = "N/A"
                item['OnTheRoadPrice'] = OnTheRoadPrice
                item['OptionalPurchase_FinalPayment'] = OptionalPurchase_FinalPayment
                item['AmountofCredit'] = AmountofCredit
                item['DurationofAgreement'] = DurationofAgreement
                item['TotalAmountPayable'] = TotalAmountPayable
                item['OptionToPurchase_PurchaseActivationFee'] = "N/A"
                item['RepresentativeAPR'] = RepresentativeAPR
                item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
                item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
                item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
                item['OfferExpiryDate'] = '05/07/2022'
                item['RetailCashPrice'] = OnTheRoadPrice
                item['CarimageURL'] = imageurl
                item['WebpageURL'] = response.url
                item['DebugMode'] = self.Debug_Mode
                item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
                try:
                    item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
                except:
                    item['DepositPercent'] = float()
                yield item


    def parse_bch_offers_link(self, response):
        """BCH OFFERS/ LEASING/ Only cars
        """
        path = response.xpath('//div[@id="cars"]//div[@class="row medium-collapse grid-enable-spacing"]/div[@class="small-12 medium-3 columns"]')
        for url in path:
           imageURL = self.getText(url, './/picture//img/@srcset')
           CarimageURL = response.urljoin(imageURL)
           href = self.getText(url, './a/@href')
           href = response.urljoin(href)
           # print("url", response.url)
           # print("href", href)
           # input("stop")
           yield Request(href, callback=self.parse_bch_offers_data, headers=self.headers, meta={"CarimageURL":CarimageURL})

    def parse_bch_offers_data(self, response):

        """BCH OFFERS
        """
        CarimageURL = response.meta['CarimageURL']
        modelPrefix = self.getText(response, '//h2[@class="header q-headline q-rte-container"]//sub/text()')
        if not modelPrefix:
            modelPrefix = self.getText(response, '//h2[@class="header q-headline q-rte-container"]/text()')
        modelPostfix = self.getText(response, '//div[@class="q-title"]/h4//text()')
        CarModel = modelPrefix +' '+modelPostfix

        # MonthlyPayment = self.getText(response, '//div[@class="q-title"]/h4//b//text()')
        # if "Business Contract Hire Example" in MonthlyPayment:
        MonthlyPayment = self.getText(response, '//div[@class="q-content "]//ul/li//span[contains(text(), "VAT / mont")]//text()')
        if not MonthlyPayment:
            MonthlyPayment = self.getText(response, '//div[@class="q-content "]//ul/li//span/b[contains(text(), "VAT / month")]//text()')


        DurationofAgreement = self.getText(response, '//div[@class="q-content "]/p//span[contains(text(), "Month term")]//text()')
        if not DurationofAgreement:
            DurationofAgreement = self.getText(response, '//div[@class="q-content "]/p//span[contains(text(), "monthly rentals")]//text()')
        if not DurationofAgreement:
            DurationofAgreement = self.getText(response, '//div[@class="q-content "]/p//span[contains(text(), "month term")]//text()')
        if not DurationofAgreement:
            DurationofAgreement = self.getText(response, '//div[@class="q-content "]//ul/li//span[contains(text(), "month term")]//text()')


        CustomerDeposit = self.getText(response, '//div[@class="q-content "]/p//span[contains(text(), "nitial rental")]//text()')
        if not CustomerDeposit:
            CustomerDeposit = self.getText(response, '//div[@class="q-content "]//ul/li//span[contains(text(), "nitial rental")]//text()')

        AnnualMileage = self.getText(response, '//div[@class="q-content "]/p//span[contains(text(), "Annual mileage: ")]//text()')
        if not AnnualMileage:
            AnnualMileage = self.getText(response, '//div[@class="q-content "]/p//span[contains(text(), "miles per year")]//text()')
        if not AnnualMileage:
            AnnualMileage = self.getText(response, '//div[@class="q-content "]//ul/li//span[contains(text(), "miles per year")]//text()')    

        # offerExp = self.getTextAll(response, '//div[@class="q-legal-text-inner"]//p//text()')
        # if "Orders from" in offerExp:
        #     offerExp = offerExp.split("Orders from ")[1].split("to")[0].strip()
        #     OfferExpiryDate = self.dateMatcher(offerExp)[0]
        # # offerExp = offerExp.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "").replace("6th", "")
        # else:
        #     OfferExpiryDate = 'N/A'    
        OfferExpiryDate = '05/07/2022'
        # print("url", response.url)
        # print("CarModel", CarModel)
        # print("MonthlyPayment", MonthlyPayment)
        # print("DurationofAgreement", DurationofAgreement)
        # print("CustomerDeposit", CustomerDeposit)
        # print("offerExp", OfferExpiryDate)
        # input("stop")

        item = CarItem()
        item['CarMake'] = 'Vauxhall'
        item['CarModel'] = self.remove_special_char_on_excel(CarModel)
        if "combo-life" in response.url or "vivaro" in response.url:
            item['TypeofFinance'] = self.get_type_of_finance('Commercial Contract Hire')
        else:
            item['TypeofFinance'] = self.get_type_of_finance('BCH')
        item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment.split("/")[0])
        item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit.split("i")[0])
        item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = 'N/A'
        item['OptionalPurchase_FinalPayment'] = 'N/A'
        item['AmountofCredit'] = 'N/A'
        item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
        item['TotalAmountPayable'] = 'N/A'
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = 'N/A'
        item['FixedInterestRate_RateofinterestPA'] ='N/A'
        item['ExcessMilageCharge'] = 'N/A'
        item['AverageMilesPerYear'] = self.remove_percentage_sign(AnnualMileage)
        item['OfferExpiryDate'] = OfferExpiryDate
        item['RetailCashPrice'] = 'N/A'
        item['CarimageURL'] = CarimageURL
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        yield item


    def parse_electric_model(self, response):

        """Electric Car E Corsa and Grandland
        """
        CarModel = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Model")]/following-sibling::td/text()')
        if not CarModel:
            CarModel = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Model")]/following-sibling::td/b/text()')
        #
        # print("resp", response.url)
        # print("model", CarModel)
        # input("stop")
        MonthlyPayment = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "monthly payments")]/following-sibling::td/text()')
        OnTheRoadPrice = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "On-the-road cash price")]/following-sibling::td/text()')
        if not OnTheRoadPrice:
            OnTheRoadPrice = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "On-the-road cash price")]/following-sibling::td/b/text()')


        RetailerDepositContribution = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Deposit contribution") or contains(text(), "deposit contribution")]/following-sibling::td/text()')
        if not RetailerDepositContribution:
            RetailerDepositContribution = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Deposit contribution") or contains(text(), "deposit contribution")]/following-sibling::td/b/text()')


        CustomerDeposit = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Customer deposit") or contains(text(), "Customer cash deposit")]/following-sibling::td//text()')
        if not CustomerDeposit:
            CustomerDeposit = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Customer deposit")]/following-sibling::td/b/text()')
        if not CustomerDeposit:
            CustomerDeposit = response.xpath('//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Customer deposit") or contains(text(), "Customer cash deposit")]/following-sibling::td//text()').extract()
            if len(CustomerDeposit) > 1:
                CustomerDeposit = CustomerDeposit[2]
         
        
        AmountofCredit = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/text()')
        if not AmountofCredit:
            AmountofCredit = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/b/text()')

        TotalAmountPayable = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/text()')
        OptionalPurchase_FinalPayment = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Optional final payment")]/following-sibling::td/text()')
        FixedInterestRate_RateofinterestPA = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Fixed rate of interest")]/following-sibling::td/text()')
        AverageMilesPerYear = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Mileage per annum") or contains(text(), "Annual mileage")]/following-sibling::td/text()')
        ExcessMilageCharge = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Excess mileage charge")]/following-sibling::td/text()')
        DurationofAgreement = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Duration of agreement")]/following-sibling::td/text()')
        RepresentativeAPR = self.getText(response, '//div[@class="ht-content flex-item"]//table/tbody/tr/td[contains(text(), "Representative APR") or contains(text(), "APR%")]/following-sibling::td/text()')

        item = CarItem()
        item['CarMake'] = 'Vauxhall'
        item['CarModel'] = self.remove_special_char_on_excel(CarModel)
        if "vans/" in response.url:
            item['TypeofFinance'] = self.get_type_of_finance('Commercial Contract Hire')
        else:
            item['TypeofFinance'] = self.get_type_of_finance('PCP')
        item['MonthlyPayment'] = self.remove_gbp(MonthlyPayment)
        item['CustomerDeposit'] = self.remove_gbp(CustomerDeposit)
        # item['CustomerDeposit'] = CustomerDeposit
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
        item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
        item['FixedInterestRate_RateofinterestPA'] = self.remove_percentage_sign(FixedInterestRate_RateofinterestPA)
        if ExcessMilageCharge:
            item['ExcessMilageCharge'] = self.remove_percentage_sign(ExcessMilageCharge)
        else:
            item['ExcessMilageCharge'] = 'N/A'
        if AverageMilesPerYear:
            item['AverageMilesPerYear'] = self.remove_percentage_sign(AverageMilesPerYear)
        else:
            item['AverageMilesPerYear'] = 'N/A'
        item['OfferExpiryDate'] = '05/07/2022'
        item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
        if "Crossland" in str(item['CarModel']):
            item['CarimageURL'] = 'https://www.vauxhall.co.uk/content/dam/vauxhall/Home/Cars/new-crossland/BBCs/New-Crossland-SE-White-Jade.png?imwidth=431'
        elif "Grandland" in str(item['CarModel']):
            item['CarimageURL'] = 'https://www.vauxhall.co.uk/content/dam/vauxhall/Home/Cars/Grandland_X/BBC/glx-diamond-black-576x322.png?imwidth=431'
        else:
            item['CarimageURL'] = ''
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        if item['MonthlyPayment'] != '':
            yield item



    def parse_specific_vans(self, response):
        """
        VANS Offer (Vivaro)
        """
        CarimageURL = response.meta['CarimageURL']
        van_model = self.getText(response, "//div[@class='q-header-addition q-rte-container']/text()")
        if not van_model:
            van_model = self.getText(response, "//h2[@class='header q-headline q-rte-container']/sub/text()")
        MonthlyPayment = self.remove_gbp(self.getText(response, '//table/tbody/tr/td[contains(text(), "72 monthly payments of")]/following-sibling::td/text()'))
        OnTheRoadPrice = self.remove_gbp(self.getText(response, '//table/tbody/tr/td[contains(text(), "On-the-road cash price including customer saving")]/following-sibling::td/text()'))
        if not OnTheRoadPrice:
            OnTheRoadPrice = self.remove_gbp(self.getText(response, '//table/tbody/tr/td[contains(text(), "On-the-road cash price including customer saving")]/following-sibling::td/b/text()'))
        CustomerDeposit = self.remove_gbp(self.getText(response, '//table/tbody/tr/td[contains(text(), "Customer deposit") or contains(text(), "Customer Deposit")]/following-sibling::td/text()'))
        if not CustomerDeposit:
            CustomerDeposit = self.remove_gbp(self.getText(response, '//table/tbody/tr/td[contains(text(), "Customer deposit") or contains(text(), "Customer Deposit")]/following-sibling::td/b/text()'))
        AmountofCredit = self.remove_gbp(self.getText(response, '//table/tbody/tr/td[contains(text(), "Total amount of credit")]/following-sibling::td/text()'))
        TotalAmountPayable = self.remove_gbp(self.getText(response, '//table/tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/text()'))
        if not TotalAmountPayable:
            TotalAmountPayable = self.remove_gbp(self.getText(response, '//table/tbody/tr/td[contains(text(), "Total amount payable")]/following-sibling::td/b/text()'))
        Duration = self.getText(response, '//table/tbody/tr/td[contains(text(), "Duration of agreement")]/following-sibling::td/text()')
        DurationofAgreement = Duration.split("months")[0]
        apr = self.getText(response, '//table/tbody/tr/td[contains(text(), "APR")]/following-sibling::td/text()')
        RepresentativeAPR   = apr.split("APR")[0]

        item = CarItem()
        item['CarMake'] = 'Vauxhall'
        item['CarModel'] = self.remove_special_char_on_excel(van_model)
        item['TypeofFinance'] = self.get_type_of_finance('PCP')
        item['MonthlyPayment'] = MonthlyPayment
        item['CustomerDeposit'] = CustomerDeposit
        item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = OnTheRoadPrice
        item['OptionalPurchase_FinalPayment'] = 'N/A'
        item['AmountofCredit'] = AmountofCredit
        item['DurationofAgreement'] = self.remove_percentage_sign(DurationofAgreement)
        item['TotalAmountPayable'] = TotalAmountPayable
        item['OptionToPurchase_PurchaseActivationFee'] = ''
        item['RepresentativeAPR'] = self.remove_percentage_sign(RepresentativeAPR)
        item['FixedInterestRate_RateofinterestPA'] = 'N/A'
        item['ExcessMilageCharge'] = 'N/A'
        item['AverageMilesPerYear'] = 'N/A'
        item['OfferExpiryDate'] = '05/07/2022'
        item['RetailCashPrice'] = OnTheRoadPrice
        item['CarimageURL'] = CarimageURL
        item['WebpageURL'] = response.url
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        if item['MonthlyPayment'] != '':
            yield item



    def parse_model(self, response):
        jO = json.loads(response.body)

        # print("jO:", jO)
        # input("wait here:")

        for key, value in jO.items():

            model = key
            trims = value["ser_d"]

            for trimId, trim in trims.items():
                mpvs_d = trim["mpvs_d"]

                for mpvs_Id, mpvs in mpvs_d.items():

                    mpvs_xml_id = mpvs_Id.replace('  ', "__")
                    # prod_base = "http://configurator-eu.ext.gm.com"
                    prod_base = "http://tools.vauxhall.co.uk"
                    callback_url = "/vcservices/rest/vauxhall/GB/b2c/en/" +\
                                    model.split('_')[0] + "/" + model.split('_')[2] + "/" +\
                                    model.split('_')[0] + '_' + model.split('_')[1] +\
                                    "/financeCalculator/"+mpvs_xml_id+".xml?series=" + trimId.replace(' ', "+") + \
                                    "&mpv=" + mpvs_Id

                    spc_link = "https://finance-calculator.vauxhall.co.uk/financeCalc/calculator?source=ffc&callback=" + \
                                 (prod_base + callback_url)

                    # print("model:", spc_link)
                    # print("res:", response.url)
                    # input("wait here:")

                    # print("spc_link:", spc_link)
                    # input("wait here:")
                    # print("response: ", response.url)
                    # print("callback_url: ", callback_url)
                    # print("spc_link: ", spc_link)
                    # print("trimId: ", mpvs['price'])
                    # print("mpvs_Id: ", mpvs_Id)
                    # input("wait here:")

                    # print("spc_link: ", spc_link)
                    # print("prod_base: ",prod_base)
                    # print("callback_url: ",callback_url)
                    # print("price: ", mpvs['price'])
                    # input("wait here:")
                    yield Request(spc_link, callback=self.call_calculate, headers=self.headers, meta={'price': mpvs['price']})

    def call_calculate(self, response):

        if response.status == 200:
            capcode = self.getText(response, '//input[@id="input_capcode"]/@value')


            capcode = capcode.replace(' ', "+")
            if " " in capcode:
                capcode = capcode.replace(' ', "+")
            elif "  " in capcode:
                capcode = capcode.replace('  ', "++")
            if "VAIN15DES5HPTM" in capcode:
                capcode = capcode.replace('  ', "++")


            # price =  self.getText(response, '//input[@id="vauxhallRRP"]/@value')
            ### No use  above price xpath###


            terms = ['24','36','48']
            for term in terms:

                html = response.body.decode('utf-8')

                offerExptext = self.getTextAll(response, '//script[@type="text/javascript"]//text()')
                offerExp = offerExptext.replace("31st", "31").replace("30th", "30").replace("29th", "29").replace("28th", "").replace("6th", "")
                OfferExpiryDate = self.dateMatcher(offerExp)[3]

                ### Offer Expiry ###
                # exp = self.getTextAll(response, '//script[@type="text/javascript"]//text()')
                # offer_exp = exp.split("         plans =")[1].split("};")[0].split("Orders or registrations from")[1].split(".")[0].split("to")[1]

                # offer_exp = exp.split("         plans =")[1].split("};")[0].split(" from 2 October to")[0].split(". Vauxhall Motors")[0]

                # print("html: ", html)
                # print("capcode: ", capcode)
                # # # print("type: ", type(offer_exp))
                # print("price: ", response.url)
                # input("wait here:")

                ### Offer Expiry ###
                img = self.reText(html, r'"fi:imageURL.":."(.*?)."')
                img = response.urljoin(img)
                model_car = self.getText(response, '//span[@class="model_car"]/text()')
                model_door = self.reText(html, r'"fi:bodystyle.":{[^}]+"fi:label.":."([^"]+)."')
                model_edition = self.reText(html, r'"fi:trimLevel.":{[^}]+"fi:label.":."([^"]+)."')
                model_engine = self.reText(html, r'"fi:enginePrice.":{[^}]+"fi:label.":."([^"]+)."')
                # price = self.reText(html, r'"fi:formatted.":{[^}]+"fi:value.":."([^"]+)."')

                price = self.reText(html, r'fi:totalPrice.":{[^}]+"fi:formatted.":."([^"]\d+[0])')

                # price = self.reText(html, r'fi:enginePrice.":{[^}]+"fi:formatted.":."([^"]\d+)') ### OTR price


                ############ BY SPLIT HTML GET OTR PRICE ############# HM
                # pricess = html.split("Final RRP (incl. VAT)")[1].split("\"}")[0]
                # prices = re.findall(r'(?<!\d\.)\b\d+(?:,\d+)?\b(?!\.\d)', pricess)[0]
                ############ BY SPLIT HTML GET OTR PRICE ############# HM

                deposit_cont = html.split("var pcpFda = ")[1].split(";")[0]
                # print("html: ", html)
                # print("price: ", price)
                # print("prices: ", prices)
                # # print("type: ", type(offer_exp))
                # print("price: ", response.url)
                # input("wait here:")

                # print("img: ", img)
                # print("model_car: ", model_car)
                # print("model_door: ", model_door)
                # print("model_edition: ", model_edition)
                # print("model_engine: ", deposit_cont)
                # print("price: ", response.url)
                # input("wait here:")
                try:
                    if "'" in deposit_cont:
                        deposit_cont = (deposit_cont.replace("'",""))
                    else:
                        deposit_cont = int(deposit_cont)
                    price_web_url = (int(price) - int(deposit_cont))
                except Exception as e:
                    print("e: ", e )
                    price_web_url = price
                    deposit_cont = int()

                interest = str()

                if "altPlanAPRTrue" in html:
                    interest = html.split('altPlanAPRTrue":')[1].split('%"')[0]
                    interest = interest.replace('"', '')
                # print("interest: ", interest)
                # input("wait here:")
                ExcessMileage = self.getText(response, '//div[@class="data-pair clearfix"]/div[contains(text(), "Excess mileage")]/following-sibling::div/text()')
                # print("ExcessMileage: ", ExcessMileage)
                # input('wait here:')

                url = 'https://finance-calculator.vauxhall.co.uk/financeCalc/en/uk/spccalculator/json/?VehicleCode=' + capcode +\
                '&CostPrice=' + str(price_web_url) + '&OptionAmount=0&Deposit=0&Term='+str(term)+'&AnnualMileage=5000'

                # print('url: ', response.url)
                # # print('html: ', html)
                # print('url: ', url)
                # # print('prices: ', prices)
                # # print('deposit_cont: ', int(deposit_cont.replace("'","")))
                # input("wait here:")

                model = '%s %s %s %s' % (model_car, model_door, model_edition, model_engine)
                yield Request(url, callback=self.parse_finance, headers=self.headers,dont_filter=True, meta={
                		'model': model,
                		'img': img,
                		'href': response.url,
                        'price': price,
                        'deposit_cont': deposit_cont,
                        'interest': interest,
                        'ExcessMileage': ExcessMileage,
                        "OfferExpiryDate":OfferExpiryDate
                        # 'offer_exp':offer_exp
                	})

    def parse_finance(self, response):
        jO = json.loads(response.body)
        OnTheRoadPrice = response.meta.get('price')
        deposit_cont = response.meta.get('deposit_cont')
        interest = response.meta.get('interest')
        href = response.meta.get('href')
        ExcessMileage = response.meta.get('ExcessMileage')
        OfferExpiryDate = response.meta.get('OfferExpiryDate')
        # offer_exp = response.meta.get('offer_exp')
        # print("jO:", jO)
        # input("wait here:")
        try:
            quote = jO["QuoteResponse"].get("Vehicles").get("Vehicle").get("Quotes").get("Quote")

        except:
            return
        if isinstance(quote, list):
            detail = None
            for q in quote:
                if 'PlanType' in q and 'Payment' in q:
                    if q['PlanType'] == 'WEBCALC FLEXI':
                        continue
                    else:
                        detail = q
                # print("q:" , q)
                # print("PlanType:" , q['PlanType'])
                # print("href: ", href)
                # input("wait here:")
                # if q['PlanType'] == 'WEBCALC FLEXI':
                #     continue
                # else:
                #     detail = q

                # if 'PlanType' in q and 'Payment' in q:
                #
                #     detail = q
                #     break

        else:
            detail = quote

        if detail == None:
            return
        elif len(detail) == 5:
            return
        # print("detail: ", detail)
        # print("detail: ", len(detail))
        # input("wait here:")
        # Parse data here
        item = CarItem()
        item['CarMake'] = 'Vauxhall'
        Carmodel = response.meta.get('model')
        item['CarModel'] = self.remove_special_char_on_excel(response.meta.get('model'))
        item['TypeofFinance'] = self.get_type_of_finance('PCP')
        item['MonthlyPayment'] = self.make_two_digit_no_vauxhall(detail.get('Payment'))
        if item['MonthlyPayment']:
            item['MonthlyPayment'] = float(item['MonthlyPayment'])
        item['CustomerDeposit'] = self.make_two_digit_no_vauxhall(detail.get('Deposit'))
        if item['CustomerDeposit']:
            item['CustomerDeposit'] = float(item['CustomerDeposit'])
        if int(deposit_cont):
            item['RetailerDepositContribution'] = self.make_two_digit_no_vauxhall(str(deposit_cont))
        else:
            item['RetailerDepositContribution'] = 'N/A'
        item['OnTheRoadPrice'] = self.remove_gbp(OnTheRoadPrice)
        if item['OnTheRoadPrice']:
            item['OnTheRoadPrice'] = float(item['OnTheRoadPrice'])
        item['OptionalPurchase_FinalPayment'] = self.remove_gbp(detail.get('FinalPayment'))
        item['AmountofCredit'] = self.remove_gbp(detail.get('AmountFinanced'))
        item['DurationofAgreement'] = self.remove_percentage_sign(detail.get('Term'))
        TotalAmountPayable = float(detail.get('TotalAmountPayable')) + float(deposit_cont)
        item['TotalAmountPayable'] = self.remove_gbp(TotalAmountPayable)
        # item['OptionToPurchase_PurchaseActivationFee'] = self.remove_gbp(detail.get('FinalPayment'))
        item['OptionToPurchase_PurchaseActivationFee'] = 'N/A'
        item['RepresentativeAPR'] = detail.get('APR')
        item['FixedInterestRate_RateofinterestPA'] = '4.79'
        item['ExcessMilageCharge'] = self.remove_percentage_sign(self.remove_gbp(ExcessMileage))
        item['AverageMilesPerYear'] = self.remove_percentage_sign(detail.get('AnnualMileage'))
        item['OfferExpiryDate'] = OfferExpiryDate ### '2 Apr 2020'
        item['RetailCashPrice'] = self.remove_gbp(OnTheRoadPrice)
        item['CarimageURL'] = response.meta.get('img')
        item['WebpageURL'] = response.meta.get('href')
        item['DebugMode'] = self.Debug_Mode
        item['FinalPaymentPercent'] = self.get_percent(item['OptionalPurchase_FinalPayment'], item['OnTheRoadPrice'])
        try:
            item['DepositPercent'] =  self.get_percent((item['CustomerDeposit']+item['RetailerDepositContribution']), item['OnTheRoadPrice'])
        except:
            item['DepositPercent'] = float()
        if item['MonthlyPayment'] != '':
            # print("detail:" , detail)
            # print("item: ", item)
            # print("url: ", response.url)
            # input("wait here:")
            yield item
