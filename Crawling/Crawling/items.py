# -*- coding: utf-8 -*-
"""
    Scrapy Items
"""

from scrapy import Field, Item


class ProductItem(Item):
    product_name = Field()
    product_price = Field()
    product_url = Field()
    product_subtitle = Field()
    product_category = Field()
    product_description = Field()
    product_ingredients = Field()
    product_image_url = Field()
    pass
