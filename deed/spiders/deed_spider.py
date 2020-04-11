import scrapy
import re
from datetime import datetime


class DeedSpider(scrapy.Spider):
    name = "deed"
    allowed_domains = ['www.tauntondeeds.com']
    start_urls = ['http://www.tauntondeeds.com/Searches/ImageSearch.aspx']

    def parse(self, response):
        request_url = 'http://www.tauntondeeds.com/Searches/ImageSearch.aspx'
        params = {
            '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first(),
            '__VIEWSTATEGENERATOR': response.css('input#__VIEWSTATE::attr(value)').extract_first(),
            "ctl00$cphMainContent$txtLCSTartDate$dateInput": "2020-01-01-00-00-00",
            "ctl00$cphMainContent$txtLCEndDate$dateInput": "2020-04-10-00-00-00",
            "ctl00$cphMainContent$ddlLCDocumentType$vddlDropDown": "101627",
            "ctl00$cphMainContent$btnSearchLC": "Search+Land+Court"}

        yield scrapy.FormRequest(
            request_url, method="POST",
            callback=self.parse_result, formdata=params)

    def parse_result(self, response):
        # next_page = response.css('tr.gridPager a::attr(href)').extract_first()
        for deed_row in response.xpath('//table[@class="grid"]/tr[not(contains(@class,"gridHeader")) '
                                  'and not(contains(@class, "gridPager"))]'):
            deed = {}
            if deed_row.css('td::text')[1].extract().strip() is None:
                deed['date'] = None
            else:
                deed['date'] = deed_row.css('td::text')[1].extract().strip()
                deed['date'] = datetime.strptime(deed['date'], '%m/%d/%Y')

            if deed_row.css('td::text')[2].extract().strip() is None:
                deed['type'] = None
            else:
                deed['type'] = deed_row.css('td::text')[2].extract().strip()

            if deed_row.css('td::text')[3].extract().strip() is None:
                deed['book'] = None
            else:
                deed['book'] = deed_row.css('td::text')[3].extract().strip()

            if deed_row.css('td::text')[4].extract().strip() is None:
                deed['page_num'] = None
            else:
                deed['page_num'] = deed_row.css('td::text')[4].extract().strip()

            if deed_row.css('td::text')[5].extract().strip() is None:
                deed['doc_num'] = None
            else:
                deed['doc_num'] = deed_row.css('td::text')[5].extract().strip()

            if deed_row.css('td::text')[6].extract().strip() is None:
                deed['city'] = None
            else:
                deed['city'] = deed_row.css('td::text')[6].extract().strip()

            if deed_row.css('span::text').extract()[0].strip() is None:
                deed['description'] = None
            else:
                deed['description'] = deed_row.css('span::text').extract()[0].strip()

            if ''.join(re.findall(r"\d+\.\d+", deed_row.css('span::text').extract()[0])) is '':
                deed['cost'] = None
            else:
                deed['cost'] = float(''.join(re.findall(r"\d+\.\d+", deed_row.css('span::text').extract()[0])))

            if ''.join(re.findall(r"\d+\s\D+\s['AVE','RD','ST']\S", deed_row.css('span::text').extract()[0])) is '':
                deed['street_address'] = None
            else:
                deed['street_address'] = ''.join(re.findall(r"\d+\s\D+\s['AVE','RD','ST']\S", deed_row.css('span::text').extract()[0]))

            if ''.join(re.findall(r"\d{5}-.", deed_row.css('span::text').extract()[0])) is '':
                deed['zip'] = None
            else:
                deed['zip'] = ''.join(re.findall(r"\d{5}-.", deed_row.css('span::text').extract()[0]))

            if ''.join(re.findall(r"(?<=STATE\s)\w+", deed_row.css('span::text').extract()[0])) is '':
                deed['state'] = None
            else:
                deed['state'] = ''.join(re.findall(r"(?<=STATE\s)\w+", deed_row.css('span::text').extract()[0]))

            yield deed

