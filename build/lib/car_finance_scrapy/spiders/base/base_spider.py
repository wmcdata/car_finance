# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request, FormRequest
from scrapy.spiders import CrawlSpider
from car_finance_scrapy.items import *
from scrapy import Selector
from scrapy.loader import ItemLoader
# from scrapy.conf import settings

import urllib
import csv
import json
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin
from time import gmtime, strftime
import requests
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

from itertools import tee, islice, chain
from dateparser.search import search_dates
from w3lib.http import basic_auth_header

class BaseSpider(CrawlSpider):
    """ Spider for site :
    """
    name = "base_spider"


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

# 
    headersLexus = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/95.0.4638.50 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Proxy-Authorization': basic_auth_header('watchmycompetitor', 'dmt276gnw845')
    }

    headers_volvo = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G920A) AppleWebKit (KHTML, like Gecko) Chrome Mobile Safari (compatible; AdsBot-Google-Mobile; +http://www.google.com/mobile/adsbot.html)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Proxy-Authorization': basic_auth_header('watchmycompetitor', 'dmt276gnw845')
    }

    headers_toyota = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G920A) AppleWebKit (KHTML, like Gecko) Chrome Mobile Safari (compatible; AdsBot-Google-Mobile; +http://www.google.com/mobile/adsbot.html)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Proxy-Authorization': basic_auth_header('watchmycompetitor', 'dmt276gnw845')
    }

    # USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36"
    headers_ajax = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type':'application/json; charset=UTF-8',
        'X-Requested-With':'XMLHttpRequest'
    }

    GOOGLE_GEOCODE_URL = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false'


    ### Debug Mode 'True' means Testing mode
    ### Debug Mode 'False' means 'Going to Live'

    Debug_Mode = 'False'


    def __init__(self):
        settings.set('RETRY_HTTP_CODES', [503, 504, 400, 408, 404] )
        settings.set('RETRY_TIMES', 5)
        settings.set('REDIRECT_ENABLED', True)
        settings.set('METAREFRESH_ENABLED', True)
        self.replace_triggers = ['<strong>', '</strong>']
        self.strip_triggers = ['', ' ', ',', '\n', ' ']


    def removeSpace(self, text):
        """ Function for remove space of text
        """
        return re.sub(r'(\s+)', ' ', text).strip()

    def remove_special_char_on_excel(self, text):
        """ Function for Capital first latter of every word
        """
        if text:
            if "–" in text:
                text  = text.replace("–", "-")
            if "’" in text:
                text = text.replace("’", "'")
            if "é" in text:
                text = text.replace("é", "e")
            if "‎," in text:
                text = text.replace(",", ",")
            if "&nbsp;" in text:
                text = text.replace("&nbsp;", " ")
            if "Q2 S" in text:
                text = text.replace("Q2 S", "Q2 S")
            if " A" in text:
                text = text.replace(" A", " A")
            if " S" in text:
                text = text.replace(" S", " S")
            if "†" in text:
                text = text.replace("†", "")
            if "*" in text:
                text = text.replace("*", "")
            if "®" in text:
                text = text.replace("®", "")
            if "Â®" in text:
                text = text.replace("Â®", "")
            if "^" in text:
                text = text.replace("^", "")
            if "Š" in text:
                text = text.replace("Š", "S")
            if "–" in text:
                text = text.replace("–", "-")
            if "ò" in text:
                text = text.replace("ò", "o")
            if "Ã‹" in text:
                text = text.replace("Ã‹", "E")
            if "Ë" in text:
                text = text.replace("Ë", "E")
            if "S&amp;S" in text:
                text = text.replace("S&amp;S", "S&S")
            if "manual " in text:
                text = text.replace("manual ","manual ")
            return text.strip()


    # parse int or float (when it contains a ',', '.')
    def parse_digit__(self, text):
        if text is not None:
            if text.find(',') != -1:
                return float(text.replace(',', '.'))
            elif text.find('.') != -1:
                return float(text)
            else:
                return int(text)
        else:
            return -1


    # def years_to_month(self, text):
    #     """ Function for remove space of text
    #     """
    #     if "Years" in text:
    #         text = text.split('Years')[0]
    #         month = (text*12)
    #         return month

    # def get_type_of_finance(self, text):
    #     type_of_finance = str()
        # if (("Business Contract Hire" == text) or ("Contract Hire" == text) or ("Contract Hire Finance" == text) or ("BCH" == text) or ("BUSINESS CONTRACT HIRE" == text) or ("CH" == text) or ("CONTRACT_HIRE" == text) or ("CONTRACT HIRE" == text)):
    #         type_of_finance = "Contract Hire"
    #     elif (("Finance Lease" == text) or ("Lease" == text)):
    #         type_of_finance = "Finance Lease"
    #     elif (("Hire Purchase" == text) or ("HIRE PURContract HireASE" == text) or ("HP" == text) or ("HIRE PURCHASE" == text) or ("BHP" == text) or ("Business Hire Purchase" == text) or ("Personal Hire Purchase" == text)):
    #         type_of_finance = "Hire Purchase"
    #     elif (("PContract Hire" == text) or ("Personal Contract Hire" == text) or ("PERSONAL CONTRACT HIRE" == text)):
    #         type_of_finance = "Personal Contract Hire"
    #     elif (("PCP" == text) or ("Acquire with Balloon" == text) or ("Passport Finance Product" == text) or ("PCP (High Deposit)" == text) or  ("PCP (Low Deposit)" == text) or ("PCP (Medium Deposit)" == text) or ("Personal Contract Purchase" == text) or ("PERSONAL CONTRACT PURCHASE" == text) or ("Acquire with balloon" == text)
    #     or ("Personal Contract Plan" == text) or ("PERSONAL CONTRACT PURContract HireASE" == text) or ("Acquire with balloon" == text) or ("Solutions PCP" == text) or ("Personal PCP" == text) or ("Agility (Personal Contract Plan)" == text)):
    #         type_of_finance = "PCP"
    #     return type_of_finance

    def get_type_of_finance(self, text):
        type_of_finance = str()
        if (("Business Contract Hire" == text) or ("BCH" == text) or ("BUSINESS CONTRACT HIRE" == text) or ("bch" == text)):
            type_of_finance = "Business Contract Hire"
        elif (("Contract Hire" == text) or ("Contract Hire Finance" == text) or ("CH" == text) or ("CONTRACT_HIRE" == text) or ("CONTRACT HIRE" == text)):
            type_of_finance = "Contract Hire"
        elif (("Finance Lease" == text) or ("Lease" == text)):
            type_of_finance = "Finance Lease"
        elif (("Hire Purchase" == text) or ("HIRE PURContract HireASE" == text) or ("HP" == text) or ("HIRE PURCHASE" == text) or ("BHP" == text) or ("Business Hire Purchase" == text) or ("Personal Hire Purchase" == text)):
            type_of_finance = "Hire Purchase"
        elif (("PContract Hire" == text) or ("Personal Contract Hire" == text) or ("PERSONAL CONTRACT HIRE" == text) or ("PCH OFFERS" == text) or ("PCH" == text)):
            type_of_finance = "Personal Contract Hire"

        elif (("PCP" == text) or ("Acquire with Balloon" == text) or ("Passport Finance Product" == text) or ("PCP (High Deposit)" == text) or  ("PCP (Low Deposit)" == text) or ("PCP (Medium Deposit)" == text) or ("Personal Contract Purchase" == text) or ("PERSONAL CONTRACT PURCHASE" == text) or ("Acquire with balloon" == text)
        or ("Personal Contract Plan" == text) or ("PERSONAL CONTRACT PURContract HireASE" == text) or ("Acquire with balloon" == text) or ("Solutions PCP" == text) or ("Personal PCP" == text) or ("Agility (Personal Contract Plan)" == text) or ("PCP OFFERS" == text)):
            type_of_finance = "Personal Contract Purchase"
        elif (("Commercial Contract Hire" == text)):
            type_of_finance = "Commercial Contract Hire"
        return type_of_finance


    def dateMatcher(self, string, identifier=False):
        valid_from = datetime(1920, 1, 1)
        valid_to = datetime(2030, 1, 1)
        # regex for day first
        regex_day_first = '((31st|30th|29th|28th)(([1-9])|([0][1-9])|([1-2][0-9])|([3][0-1])) ([Jj]an(uary)?|[Ff]eb(ruary)?|[Mm]ar(ch)?|[Aa]pr(il)?|[Mm]ay|[Jj]une?|[Jj]uly?|[Aa]ug(ust)?|[Ss]ept?(ember)?|[Oo]ct(ober)?|[Nn]ov(ember)?|[Dd]ec(ember)?) ?(\d{4})?)|(\d{1,2}[- ]+[A-Za-z]{3,}[- ]+\d{2,4})|(\b\d{1,2}\/[\d]{1,2}\/\d{2,4})|(\d{2}-[\d]+-\d{2,4})'
        month_first_regex = '(([Jj]an(uary)?|[Ff]eb(ruary)?|[Mm]ar(ch)?|[Aa]pr(il)?|[Mm]ay|[Jj]une?|[Jj]uly?|[Aa]ug(ust)?|[Ss]ept?(ember)?|[Oo]ct(ober)?|[Nn]ov(ember)?|[Dd]ec(ember)?) (([1-9])|([0][1-9])|([1-2][0-9])|([3][0-1])), ?(\d{4})?)'
        month_first_regex_case1 = '(([Jj]an(uary)?|[Ff]eb(ruary)?|[Mm]ar(ch)?|[Aa]pr(il)?|[Mm]ay|[Jj]une?|[Jj]uly?|[Aa]ug(ust)?|[Ss]ept?(ember)?|[Oo]ct(ober)?|[Nn]ov(ember)?|[Dd]ec(ember)?) (([1-9])|([0][1-9])|([1-2][0-9])|([3][0-1])),)'
        # dates = re.findall(r"(\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4})", item)
        dt_formats = [
            ['%d', '%m', '%Y'],
            ['%d', '%b', '%Y'],
            ['%d', '%B', '%Y'],
            ['%B', '%d', '%Y'],
            ['%Y'],
            ['%d', '%b'],
            ['%d', '%B'],
            ['%b', '%d'],
            ['%B', '%d'],
            ['%b', '%Y'],
            ['%B', '%Y']

        ]

        t1, t2, t3 = tee(re.findall(r'\b\w+\b', string), 3)

        next(t2, None)
        next(t3, None)
        next(t3, None)
        triples = zip(t1, t2, t3)
        if identifier:
            valid_Dates = ""
        else:
            valid_Dates = []
        for triple in triples:
            for dt_format in dt_formats:
                try:
                    dt = datetime.strptime(' '.join(triple[:len(dt_format)]), ' '.join(dt_format))
                    if valid_from <= dt <= valid_to:
                        if identifier:
                            valid_Dates = (dt.strftime('%d/%m/%Y'))
                        else:
                            valid_Dates.append(dt.strftime('%d/%m/%Y'))
                        # return dt.strftime('%d-%m-%Y')
                        for skip in range(1, len(dt_format)):
                            try:
                                next(triples)
                            except StopIteration:
                                pass
                    break
                except ValueError:
                    pass
        if not valid_Dates:
            match = re.match(r'.*([2][0-9]{3})', string)
            if match is not None:
                if identifier:
                    if 2010 < int(match.group(1)) < 2030:
                        valid_date = match.group(1)
                        valid_Dates = (valid_date)
                else:
                    if 2010 < int(match.group(1)) < 2030:
                        valid_date = "01" + "/" + "01" + "/" + match.group(1)
                        valid_Dates.append(valid_date)
            else:
                rematch = re.search(regex_day_first, string)
                if rematch is not None:
                    rematch_findall = re.findall(regex_day_first, string)
                    if len(rematch_findall) > 1:
                        for date_string in rematch_findall:
                            valid_date = date_string[0]
                            if identifier:
                                valid_Dates = (valid_date)
                            else:
                                valid_Dates.append(valid_date)
                    else:
                        valid_date = rematch.group(1)
                        if identifier:
                            valid_Dates = (valid_date)
                        else:
                            valid_Dates.append(valid_date)
                else:
                    exp = re.compile(r'(\w+) (\d+)')
                    match_month_first = exp.search(string)
                    if match_month_first:
                        match_month_first_findall = exp.findall(string)
                        if len(match_month_first_findall) > 1:
                            for date_string in match_month_first_findall:
                                valid_date = date_string[0]
                                if identifier:
                                    valid_Dates = (valid_date)
                                else:
                                    valid_Dates.append(valid_date)
                        else:
                            valid_date = match_month_first.group()
                            if identifier:
                                valid_Dates = (valid_date)
                            else:
                                valid_Dates.append(valid_date)
                    # else:
                    #     exp = re.compile(r'(\w+)')
                    #     match_only_month = exp.search(string)
                    #     if match_only_month:
                    #         match_month_first_findall = exp.findall(string)
                    #         if identifier:
                    #             valid_Dates = match_month_first_findall
                    #         else:
                    #             valid_Dates.append(match_month_first_findall)

        return valid_Dates

    # parse int or float (when it contains a ',', '.')
    def parse_digit__(self, text):
        if text is not None:
            if text.find(',') != -1:
                return float(text.replace(',', '.'))
            elif text.find('.') != -1:
                return float(text)
            else:
                return int(text)
        else:
            return -1
# make_two_digit__remove_percent_sign
    def make_two_digit_no_vauxhall(self, text):
        """This function will remove any text like % , spaces
        and will add two digit after dot.
        """
        if text != None or text != '':
            text = re.sub("[^\d\.]", "", text)
            # print("...", text)
            # input()
            if isinstance(text, str):
                text=text.replace(',','')

            texts = float(text)
            text = format(texts,".2f")
            # # print(format(b,".2f"))
            return text.strip()

    def make_two_digit_no(self, text):
        """This function will remove any text like % , spaces
        and will add two digit after dot.
        """
        if text != None or text != '':
            text = re.sub("[^\d\.]", "", text)
            texts = float(text)
            text = format(texts,".2f")
            # # print(format(b,".2f"))
            return text.strip()        

    def make_two_digit_no_error(self, text):
        """
        will add two digit after dot.
        """
        if text != None or text != '':
            texts = float(text)
            text = format(texts,".2f")
            # print("...", texts)
            # input()
            # # print(format(b,".2f"))
            return text.strip()

    def remove_percentage_sign(self, text):
        """This function will remove any text like % , spaces
        """
        if text != None or text != '':
            text = re.sub("[^\d\.]", "", text)
            # input()
            return text.strip()

    # def get_type_of_finance(self, text):
    #     """ Function for replace Type of finance
    #     """
    #
    #     if "Acquire with Balloon" in text:
    #         text = text.replace("Acquire with Balloon", "PCP")
    #     elif "Passport Finance Product" in text:
    #         text = text.replace("Passport Finance Product", "PCP")
    #     elif "PCP (High Deposit)" in text:
    #         text = text.replace("PCP (High Deposit)", "PCP")
    #     elif "PCP (Low Deposit)" in text:
    #         text = text.replace("PCP (Low Deposit)", "PCP")
    #     elif "PCP (Medium Deposit)" in text:
    #         text = text.replace("PCP (Medium Deposit)", "PCP")
    #     elif "Personal Contract Purchase" in text:
    #         text = text.replace("Personal Contract Purchase", "PCP")
    #     elif "Personal Contract Hire" in text:
    #         text = text.replace("Personal Contract Hire", "Personal Contract Hire")
    #     elif "PERSONAL CONTRACT PURCHASE" in text:
    #         text = text.replace("PERSONAL CONTRACT PURCHASE", "PCP")
    #     elif "BCH" in text:
    #         text = text.replace("BCH", "Contract Hire")
    #     elif "BUSINESS CONTRACT HIRE" in text:
    #         text = text.replace("BUSINESS CONTRACT HIRE", "Contract Hire")
    #     elif "CH" in text:
    #         text = text.replace("CH", "Contract Hire")
    #     elif "Contract Hire Finance" in text:
    #         text = text.replace("Contract Hire Finance", "Contract Hire")
    #     elif "CONTRACT_HIRE" in text:
    #         text = text.replace("CONTRACT_HIRE", "Contract Hire")
    #     elif "Finance Lease" in text:
    #         text = text.replace("Finance Lease", "Finance Lease")
    #     elif "Hire Purchase" in text:
    #         text = text.replace("Hire Purchase", "Hire Purchase")
    #     elif "HP" in text:
    #         text = text.replace("HP", "Hire Purchase")
    #     elif "HP" in text:
    #         text = text.replace("HP", "Hire Purchase")
    #     elif "CONTRACT_HIRE" in text:
    #         text = text.replace("CONTRACT_HIRE", "Contract Hire")
    #     elif "PERSONAL CONTRACT PURContract HireASE" in text:
    #         text = text.replace("PERSONAL CONTRACT PURContract HireASE", "PCP")
    #     elif "PERSONAL CONTRACT PURCHASE" in text:
    #         text = text.replace("PERSONAL CONTRACT PURCHASE", "PCP")
    #     elif "PERSONAL CONTRACT PURContract HireASE" in text:
    #         text = text.replace("PERSONAL CONTRACT PURContract HireASE", "PCP")
    #     elif "PERSONAL CONTRACT HIRE" in text:
    #         text = text.replace("PERSONAL CONTRACT HIRE", "Contract Hire")
    #     elif "PContract Hire" in text:
    #         text = text.replace("PContract Hire", "Personal Contract Hire")
    #     elif "Acquire with balloon" in text:
    #         text = text.replace("Acquire with balloon", "PCP")
    #     elif "Personal Contract Plan" in text:
    #         text = text.replace("Personal Contract Plan", "PCP")
    #     elif "HIRE PURContract HireASE" in text:
    #         text = text.replace("HIRE PURContract HireASE", "Hire Purchase")
    #     final_text =  self.get_type_of_finances(text)
    #     return final_text



    def google_geocode(self, address):
        """ Get city, state, coutry of address by google geocode service
        """

        result = {
            'street': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': '',
            'latitude': '',
            'longitude': ''
        }

        street_number = ''

        if address == '':
            return result

        url = self.GOOGLE_GEOCODE_URL % address
        response = requests.get(url, headers=self.headers)

        jO = json.loads(response.content)

        if ('results' in jO and len(jO['results']) > 0 and \
            'address_components' in jO['results'][0]):

            for component in jO['results'][0]['address_components']:
                if 'short_name' in component and 'types' in component:

                    # street number
                    if 'street_number' in component['types']:
                        street_number= component['short_name']

                    # street name
                    elif 'route' in component['types']:
                        result['street'] = component['short_name']

                    # City
                    elif 'locality' in component['types']:
                        result['city'] = component['short_name']

                    # City alternative
                    elif not result['city'] and 'postal_town' in component['types']:
                        result['city'] = component['short_name']

                    # State
                    elif 'postal_code' in component['types']:
                        result['postal_code'] = component['short_name']

                    # State
                    elif 'administrative_area_level_1' in component['types']:
                        result['state'] = component['short_name']

                    # Country
                    elif 'country' in component['types']:
                        result['country'] = component['short_name']

        if 'results' in jO and len(jO['results']) > 0 and 'geometry' in jO['results'][0] and \
            'location' in jO['results'][0]['geometry'] and \
            'lat' in jO['results'][0]['geometry']['location']:
            result['latitude'] = jO['results'][0]['geometry']['location']['lat']

        if 'results' in jO and len(jO['results']) > 0 and 'geometry' in jO['results'][0] and \
            'location' in jO['results'][0]['geometry'] and \
            'lng' in jO['results'][0]['geometry']['location']:
            result['longitude'] = jO['results'][0]['geometry']['location']['lng']

        result['street'] = ('%s %s'%(street_number, result['street'] )).strip()
        return result

    def latlng2Address(self, lat, lng, disp=False, city=False):
        url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s' % (lat, lng)
        response = requests.get(url, headers=self.headers)

        street_number = str(); route  = str()
        city_name = str(); postal_code = str()

        jO = json.loads(response.content)
        if disp:
            print(jO['results'][0])
        try:
            for el in jO['results'][0]['address_components']:
                if "street_number" in el['types']:
                    street_number = el['long_name']
                elif "postal_code" in el['types']:
                    postal_code = el['long_name']
                elif "route" in el['types']:
                    route = el['long_name']
                if city and 'locality' in el['types']:
                    city_name = el['long_name']
        except:
            pass

        if not street_number:
            try:
                address = ','.join(jO['results'][0]['formatted_address'].split(',')[:-1])
            except IndexError as exc:
                if city:
                    return('%s %s' % (street_number, route), postal_code, city_name)
                else:
                    return('%s %s' % (street_number, route), postal_code)

            if city:
                return(address, postal_code, city_name)
            else:
                return(address, postal_code)

        if city:
            return('%s %s' % (street_number, route), postal_code, city_name)
        else:
            return('%s %s' % (street_number, route), postal_code)

    def latlng2AddressCity(self, lat, lng):
        url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s' % (lat, lng)
        response = requests.get(url, headers=self.headers)

        street_number = ''
        route  = ''
        postal_code = ''
        city = ''

        jO = json.loads(response.content)
        try:
            for el in jO['results'][0]['address_components']:
                if "street_number" in el['types']:
                    street_number = el['long_name']

                elif "postal_code" in el['types']:
                    postal_code = el['long_name']

                elif "route" in el['types']:
                    route = el['long_name']

                elif "locality" in el['types']:
                    city = el['long_name']
        except:
            print(response.content)
            pass

        return ((street_number + ' ' + route).strip(), postal_code, city)

    def removeTags(self, text):
        """ exec regex pattern on text and remove matching string at group
        """
        return re.sub(r'(<.*?>)', '', text).strip()

    def getText(self, selector, xpath):
        """ Exec xpath query on selector and return first match as string
        """
        vals = selector.xpath(xpath).extract()
        if len(vals) > 0:
            return vals[0].strip()
        else:
            return ''

    def getTexts(self, selector, xpath, dont_filter=True):
        """ Exec xpath query on selector and return all match as list of string
        """
        return [x.strip() for x in selector.xpath(xpath).extract() if dont_filter or x.strip() != '' ]

    def getTextAll(self, selector, xpath, join_string=' '):
        """ Exec xpath query on selector and return all match as string
        """
        return join_string.join( [x.strip() for x in selector.xpath(xpath).extract()] ).strip()

    def reText(self, text, pattern, group=1):
        """ exec regex pattern on text and return matching string at group
        """
        match = re.search(pattern, text)
        if match != None:
            return match.group(group)
        else:
            return ''

    def getwebcontent(self, url):
        # user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        # headers = { 'User-Agent' : user_agent }

        req = urllib2.Request(url, headers = self.headers)
        response = urllib2.urlopen(req)
        return response.read()

    def convertDateFormat(self, datestring, src_format, dst_format):
        if src_format == dst_format:
            return datestring
        return datetime.strptime(datestring, src_format).strftime(dst_format)

    def parse_date(self, datestring, formats):
        for fmt in formats:
            try:
                return datetime.strptime(datestring, fmt)
            except ValueError:
                pass

    default_xpaths=dict()

    def start_requests(self):
        yield Request(
            url = self.start_url,
            callback= self.parse_items,
            headers= self.headers
        )
    def remove_gbp(self, string):
        if (type(string) is str):
            if "£" in string:
                string = string.replace("£", "")
            elif "/td>" in string:
                string = string.replace("/td>","")
            elif "GBP" in string:
                string = string.replace("GBP","")
            elif "^" in string:
                string = string.replace("^","")
            if "VAT" in string:
                string = string.replace("VAT","")
            string = string.replace("+", "")
            string = string.replace(" ", "")
            string = string.replace(",", "")
            string = string.replace("exc", "")
            string = string.replace("*", "")
        return string





    def get_percent(self, val, divident):
        val = self.remove_gbp(val)
        divident = self.remove_gbp(divident)
        percent = float()
        if (type(val) is float) or (type(val) is int):
            val = val
        else:
            if "," in val:
                val = val.replace(",","")
                try:
                    val = float(val)
                except:
                    val = 0
            else:
                try:
                    val = float(val)
                except:
                    val = 0
        if (type(divident) is float) or (type(divident) is int):
            divident = divident
        else:
            if "," in divident:
                divident = divident.replace(",","")
                try:
                    divident = float(divident)
                except:
                    divident = 0
            else:
                try:
                    divident = float(divident)
                except:
                    divident = 0
        if type(divident) and type(val) is float:
            try:
                percent = val/divident
            except ZeroDivisionError:
                percent = 0
        else:
            percent = 0

        return round(percent, 2)

    def parse_items(self, response):
        if 'item' in self.page_xpaths:
            for href in response.xpath(self.page_xpaths['item']).extract():
                href = urljoin(response.url, href)
                yield Request(
                    url = href,
                    callback= self.parse_item,
                    headers= self.headers
                )

        if 'items' in self.page_xpaths:
            for href in response.xpath(self.page_xpaths['items']).extract():
                href = urljoin(response.url, href)
                yield Request(
                    url = href,
                    callback= self.parse_items,
                    headers= self.headers
                )

    def parse_item(self, response):
        """ Function for: Parse item
        """

        if 'item_loader' in self.page_xpaths:
            for sel in response.xpath(self.page_xpaths['item_loader']):
                yield self._parse_item(sel, response)
        else:
            yield self._parse_item(response, response)

    def _parse_item(self, sel, response):
        il = ItemLoader(item=EventItem(), response=sel)
        xpaths = self.default_xpaths.copy()
        xpaths.update(self.item_xpaths)


        for key in xpaths:
            il.add_xpath(key, xpaths[key])

        il.add_value('PropertyRoomURL', response.url)
        il.add_value('Competitor', self.competitorName)
        il.add_value('DateExtractRun', strftime("%Y-%m-%d %H:%M:%S", gmtime()))

        item = il.load_item()

        return item

    def remove_duplicates(self, mylist):
        seen = set()
        seen_add = seen.add
        return [x for x in mylist if not (x in seen or seen_add(x))]
    def chunks(l, n):
    # For item i in a range that is a length of l,
        for i in range(0, len(l), n):
        # Create an index range for l of n items:
            yield l[i:i+n]

    def filter_items(self, mystring):

        for trigger in self.replace_triggers:
            mystring = mystring.replace(trigger, str())

        for trigger in self.strip_triggers:
            mystring = mystring.strip(trigger)

        return mystring
