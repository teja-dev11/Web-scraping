# -*- coding: utf-8 -*-
"""
    KG Web Sources Utils
"""
import os
import json
import time

from scrapy.crawler import CrawlerProcess
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.utils.serialize import ScrapyJSONEncoder


DATA_PATH = os.environ.get('DATA_PATH', './data/')
scrapy_encoder = ScrapyJSONEncoder()


def get_scrapy_results(Spider):
    results = []

    def crawler_results(signal, sender, item, response, spider):
        results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_passed)

    process = CrawlerProcess()
    process.crawl(Spider)
    process.start()
    return results


def save_results(results, category, source):
    data_source_path = os.path.join(DATA_PATH, category, source)

    if not os.path.exists(data_source_path):
        os.makedirs(data_source_path)

    data = {
        'name': source,
        'category': category,
        'datetime': time.strftime("%Y-%m-%d %H:%M:%S"),
        'data': json.loads(scrapy_encoder.encode(results)),
    }

    with open(os.path.join(data_source_path, 'crawl_results.json'), 'w') as fp:
        json.dump(data, fp)
