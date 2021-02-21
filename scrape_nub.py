# -*- coding: utf-8 -*-

import time
import json
import logging
import pandas as pd

from selenium import webdriver

logger = logging.getLogger(__name__)

"""Scraping part"""


def scrape_source(url, driver, xpath_select_box, xpath_find_element):
    logger.info("Started Scraping source url")
    crawled_results = {}
    select_box = driver.find_element_by_xpath(xpath_select_box)
    # select_box.click()
    time.sleep(3)
    options = [x for x in select_box.find_elements_by_tag_name("option")]
    for element in options:
        option_value = element.get_attribute("value")
        if option_value != '' and option_value != '-1' and len(option_value) > 0:
            driver.find_element_by_xpath(xpath_find_element.format(option_value)).click()
            driver.find_element_by_id("querySubstancias").click()
            result_table = driver.find_element_by_id('resultsTable')
            while True:
                btn_text = driver.find_element_by_id("querySubstancias").text
                if btn_text != "Searching...":
                    break
            rows = [x for x in result_table.find_elements_by_class_name("c1")]
            records = []
            for row in rows:
                temp = {}
                row.find_element_by_tag_name("a").click()
                time.sleep(5)
                common_name = driver.find_element_by_id("nome").get_attribute('value')
                smiles = driver.find_element_by_id("smiles").get_attribute('value')
                inchikey = driver.find_element_by_id("inchikey").get_attribute('value')
                # doi_ids = doi_ids = driver.find_element_by_xpath("/html/body/div[4]/div[2]/div[4]/div[1]/div[5]/div[2]").text.split("\n")
                doi_ids = driver.find_element_by_xpath('//*[@id="publicacoes"]').text.split("\n")

                temp['common_name'] = common_name
                temp['smiles'] = smiles
                temp['inchikey'] = inchikey
                temp['doi_ids'] = doi_ids
                records.append(temp)
            print(records)
            print(element.text)

            crawled_results[element.text] = records

    logger.info("Successfully completed process")
    driver.close()
    return crawled_results


def parse_nested_json(json_d):
    result = {}
    for key in json_d.keys():
        if not isinstance(json_d[key], dict):
            result[key] = json_d[key]
        else:
            result.update(parse_nested_json(json_d[key]))
    return result


if __name__ == "__main__":
    url = "https://nubbe.iq.unesp.br/portal/nubbe-search.html"
    driver = webdriver.Chrome('C:\chrome\chromedriver')
    driver.get(url)
    output_file = "result.json"

    xpath_especieSelect_select_box = '//*[@id="especieSelect"]'
    xpath_especieSelect_find_element = "//*[@id='especieSelect']/option[@value='{0}']"
    response = scrape_source(url, driver, xpath_especieSelect_select_box, xpath_especieSelect_find_element)
    with open(output_file, "w") as f:
        f.write(json.dumps(response, indent=4))
    json_data = pd.read_json("result.json")
    json_list = [j[1][0] for j in json_data.iterrows()]
    parsed_list = [parse_nested_json(j) for j in json_list]
    result = pd.DataFrame(parsed_list)
    result.to_csv("scrape_nub.csv", index=False)
