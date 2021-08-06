# -*- coding: utf-8 -*-
"""
    Sunwarrior - https://sunwarrior.com

    Run with:
        python -m kg.sources.sunwarrior

"""

import scrapy

from kg.items import ProductItem
from kg.utils import get_scrapy_results, save_results


SOURCE_NAME = 'sunwarrior'

class SunwarriorScraperSpider(scrapy.Spider):
    name = SOURCE_NAME
    start_urls = ['https://sunwarrior.com/collections/all']

    def parse(self, response):
        items = ProductItem()

        product_name = response.css('.grid-product__title a::text').extract()
        product_price = response.css('.money::text').extract()
        product_subtitle =  response.css('.short_desc::text').extract()
        product_image_url = response.css('.lazyloaded::attr(src)').extract()

        items['product_name'] = product_name
        items['product_price'] = product_price
        items['product_subtitle'] = product_subtitle
        items['product_image_url'] = product_image_url

        yield items


if __name__ == "__main__":
    results = get_scrapy_results(SunwarriorScraperSpider)
    save_results(results, 'web', SOURCE_NAME)
