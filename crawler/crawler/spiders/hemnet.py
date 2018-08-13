# -*- coding: utf-8 -*-
import scrapy
import re
import json

class HemnetSpider(scrapy.Spider):
    name = 'hemnet'
    allowed_domains = ['hemnet.se']
    start_urls = ['https://www.hemnet.se/bostader?location_ids%5B%5D=17744&item_types%5B%5D=villa&advanced=1&rooms_min=5']

    def parse(self, response):
        homes = response.xpath("//ul/li/div/a/@href")
        for home in homes.extract():
            yield scrapy.Request(response.urljoin(home), self.parse_home)

        next_page_url = response.xpath('//a[@class="next_page button button--primary"]/@href').extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_home(self, response):
        # XXX Is this really stable? Dig property info in json from the scripts
        items = {}
        for s in response.xpath("/html/body/script").extract():
            js_lst = re.search('dataLayer = (\[.*\])\;', s)
            if js_lst is None:
                continue
            js_lst = js_lst.group(1)
            lst = json.loads(js_lst)
            for dct in lst:
                if 'property' in dct:
                    items.update(dct['property'])

        for s in response.xpath("//div[@class='item property-neighbourhood__container js-listing-map']/@data-initial-data").extract():
            dct = json.loads(s)
            if dct:
                if 'property' in dct:
                    if dct['property']['id'] == items['id']:
                        items.update(dct['property'])
                        break

        return items


