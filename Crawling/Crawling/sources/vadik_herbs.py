# -*- coding: utf-8 -*-
"""
    Vadik Herbs - https://vadikherbs.com

    Run with:
        python -m kg.sources.vadik_herbs

"""
import scrapy
from scrapy.http import Request

from kg.items import ProductItem
from kg.utils import get_scrapy_results, save_results

SOURCE_NAME = 'vadik_herbs'


class VadikSpider(scrapy.Spider):
    name = SOURCE_NAME
    start_urls = [
        'https://vadikherbs.com/collections/health-packs',
        'https://vadikherbs.com/collections/cooking',
        'https://vadikherbs.com/collections/ayurvedic-herbs'
        'https://vadikherbs.com/collections/herbal-drinks',
        'https://vadikherbs.com/collections/herbal-formulas'
        'https://vadikherbs.com/collections/oils',
        'https://vadikherbs.com/collections/massage-oils',
        'https://vadikherbs.com/collections/nasya-oils-herbal-nasal-drops'
    ]

    def parse(self, response, **kwargs):
        for product in response.css('div.product-wrap'):
            try:
                print("Scraping url :{}".format(response.url))
                product_name = product.css("div.product-details span.title::text").get()
                product_price = product.css('div.product-details span.price span.money::text').get()
                description_route = product.css('a.product-info__caption').attrib["href"].split("/")[-1]
                description_url = f"{response.url}/products/{description_route}"
                print("description-url", description_url)
                yield Request(url=description_url, callback=self.parse_description,
                              meta={'item': description_route, "url": description_url},
                              cb_kwargs={"product_name": product_name, "product_price": product_price})

            except Exception as e:
                print("Error while scraping for product: {} Error:{}".format(
                    product.css("div.product-details span.title::text").get(), e))

    def parse_description(self, response, **kwargs):
        item = ProductItem()
        try:
            description_data = response.css("div.description.bottom p::text").getall()
            data = self.clean_data(data=description_data)
            contents = self.preprocess_contents(data, response)
            item["product_name"] = kwargs.get("product_name")
            item["product_price"] = "sold out" if kwargs.get("product_price") is None else kwargs.get("product_price")
            item["product_url"] = response.url
            item["product_subtitle"] = " "
            item["product_category"] = response.css("div.breadcrumb_text a::attr(title)").getall()[-1]
            item["product_description"] = contents.get("Description", '')
            item["product_ingredients"] = contents.get("Ingredients", '')
            item["product_image_url"] = response.css("div.image__container img::attr(src)").getall()[0]

        except Exception as e:
            print(e)
            raise e
        yield item

    def preprocess_contents(self, data, response):
        headings = response.css("div.description.bottom b::text").getall()
        if len(headings) == 0:
            headings = response.css("div.description.bottom p strong::text").getall()
        contents = {}
        combined = []
        for i in zip(headings, data):
            combined.append(i[0] + "-" + i[1])
        heading_keys = ["Description", "Ingredients"]
        Ingredients = ""
        if response.css("div.description.bottom li").getall():
            if response.css("div.description.bottom li span::text").getall():
                Description = " ".join(response.css("div.description.bottom li span::text").getall()).replace("\n", "")
            else:
                Description = " ".join(response.css("div.description.bottom li::text").getall()).replace("\n", "")
            if len(data) > 0:

                if [i for i in headings if "Ingredients" in i]:
                    Ingredients = data[-1]
                    Description = Description + " ".join(data)
                else:
                    Description = Description + " ".join(data)
            else:
                data = self.clean_data(data=response.css("div.a-section::text").getall())
                Ingredients = data[-1]

            contents.update({"Description": Description, "Ingredients": Ingredients})
        else:
            for ix, i in enumerate(combined):
                contents.update({heading_keys[ix]: i})
        if len(contents.get("Description", "")) == 0:
            data = " ".join(response.css("div.description.bottom p::text").getall())
            contents.update({"Description": data})

        if len(contents.get("Description", "")) < 100:
            print("ds")
        return contents

    def clean_data(self, data):

        filtered = []
        for i in data:
            if len(i) < 20:
                pass
            else:
                filtered.append(i)
        return filtered


if __name__ == "__main__":
    try:
        results = get_scrapy_results(VadikSpider)
        save_results(results, 'web', SOURCE_NAME)
    except Exception as e:
        print(e)
