# -*- coding: utf-8 -*-


import logging
import requests
import json
import os
import pandas as pd

logger = logging.getLogger(__name__)

"""Scraping part"""


def scrape_db(cache_dir):
    res = requests.get(
        'https://cwtung.kmu.edu.tw/tipdb/search_json2.php?chemical=&na=&tid=&part=All&classify=All&ch_box=all'
    )
    logger.info(f'Loaded page')
    os.makedirs(cache_dir, exist_ok=True)

    objs = res.json()
    data_dict = {}

    for obj in tqdm(objs[1:], desc='Extracting data'):
        plant_name = obj[0].replace('"', '')
        plant_part = obj[1].replace('"', '')
        chemicals = obj[4].replace('"', '')

        if plant_name not in data_dict:
            data_dict[plant_name] = {}

        if plant_part not in data_dict[plant_name]:
            data_dict[plant_name][plant_part] = []

        data_dict[plant_name][plant_part].append(chemicals)

    with open(os.path.join(cache_dir, 'results.json'), 'w') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)


def create_df(cache_dir, data_dir):
    with open(os.path.join(cache_dir, 'results.json')) as f:
        data_dict = json.load(f)

    data_df = pd.DataFrame(columns=['plant_name', 'plant_part', 'chemical_name'])

    for plant in tqdm(data_dict, desc='Creating TSV file'):
        for plant_part, chemicals in data_dict[plant].items():
            tmp_df = pd.DataFrame({
                'plant_name': plant,
                'plant_part': plant_part,
                'chemical_name': chemicals
            })
            data_df = pd.concat([data_df, tmp_df], ignore_index=True)

    data_df.to_csv(os.path.join(data_dir, 'tipdb_data.tsv'), sep='\t', index=False)
