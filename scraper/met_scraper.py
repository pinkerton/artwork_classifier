import re
import shutil

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests

DATASET_PATH = '../MetObjects.csv'


def fetch_page(url: str) -> bytes:
    response = requests.get(url, timeout=5)
    return response.content


def parse_page(content: bytes) -> str:
    page_content = BeautifulSoup(content, "html.parser")
    download_button = page_content.find(class_='utility-menu__item utility-menu__item--download')
    href = download_button.a['href']
    artwork_url = re.search('https\S+.\w', href).group(0)
    return artwork_url


def get_file_extension(url: str) -> str:
    return re.search('.(\w+)$', url).groups()[0]


def download_artwork(artwork_url: str, artwork_id: int):
    extension = get_file_extension(artwork_url)
    path = "images/{}.{}".format(artwork_id, extension)

    response = requests.get(artwork_url, stream=True, timeout=5)
    with open("images/{}.{}".format(artwork_id, extension), 'wb') as out_file:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, out_file)
    del response


def scrape():
    df = pd.read_csv(DATASET_PATH)
    public_domain = df.loc[df['Is Public Domain'] == True]
    public_domain_links = public_domain['Link Resource']
    for artwork_id, page_url in public_domain_links[:3].iteritems():
        raw_response = fetch_page(page_url)
        artwork_url = parse_page(raw_response)
        download_artwork(artwork_url, artwork_id)


if __name__ == '__main__':
    scrape()
