import os
import re
import shutil

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests

DATASET_PATH = '../MetObjects.csv'
IMAGES_PATH = 'images'
MAX_RETRIES = 3
BUCKET_THRESHOLD = 1000


def get_starting_id() -> int:
    files = os.listdir(IMAGES_PATH)
    if len(files) == 0:
        return 0
    # ['33.jpg', '330.jpg', '34.jpg'] => [33, 330, 34]
    artwork_ids = [int(filename.split('.')[0]) for filename in files]
    return max(artwork_ids)


def fetch_page(url: str) -> bytes:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
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


def log_failed_request(artwork_url: str, artwork_id: int, err: Exception):
    with open('failed.txt', 'a') as f:
        f.write("ID: {0:<10} URL: {1:<50} ERR: {}\n".format(artwork_id, artwork_url, err))


def log_successful_request(artwork_url: str, artwork_id: int):
    with open('success.txt', 'a') as f:
        f.write("ID: {0:<10} URL: {1:<50}\n".format(artwork_id, artwork_url))


def scrape():
    starting_id = get_starting_id()
    df = pd.read_csv(DATASET_PATH)
    public_domain = df.loc[df['Is Public Domain'] == True]
    sampled_artwork = public_domain.groupby('Object Name').filter(lambda x: len(x) >= BUCKET_THRESHOLD)
    remaining_artwork = sampled_artwork.loc[starting_id:]
    public_domain_links = remaining_artwork['Link Resource']
    for artwork_id, page_url in public_domain_links.iteritems():
        retries = 0
        done = False
        last_exception = None
        while not done and retries < MAX_RETRIES:
            print("Fetching {} (attempt #{})".format(artwork_id, retries))
            try:
                raw_response = fetch_page(page_url)
                artwork_url = parse_page(raw_response)
                download_artwork(artwork_url, artwork_id)
                done = True
            except requests.exceptions.RequestException as err:
                print(err)
                last_exception = err
                retries += 1

        if not done:
            log_failed_request(artwork_url, artwork_id, last_exception)
        else:
            log_successful_request(artwork_url, artwork_id)


if __name__ == '__main__':
    scrape()
