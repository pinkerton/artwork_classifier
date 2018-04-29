import numpy as np
import pandas as pd

import os

"""
This script moves previously-scraped images into a new folder if they match
our criteria to be included in analysis later (>1000 samples per Object Name).
Basically, we only want to scrape images for an Object Name (painting, vase, etc.)
if we have more than 1000 examples of them in the dataset. This script lets us avoid
re-scraping old images.
"""

DATASET_PATH = '../MetObjects.csv'
NEW_PATH = 'images'
OLD_PATH = 'old-images'
MAX_RETRIES = 3
BUCKET_THRESHOLD = 1000


if __name__ == "__main__":
    df = pd.read_csv(DATASET_PATH)
    public_domain = df.loc[df['Is Public Domain'] == True]
    buckets = public_domain.groupby('Object Name').filter(lambda x: len(x) >= BUCKET_THRESHOLD)
    public_domain_links = buckets['Link Resource']
    for artwork_id, page_url in public_domain_links.iteritems():
        old_image_path = "{}/{}.jpg".format(OLD_PATH, artwork_id)
        new_image_path = "{}/{}.jpg".format(NEW_PATH, artwork_id)
        if os.path.isfile(old_image_path):
            os.rename(old_image_path, new_image_path)
            print("Moved {}".format(artwork_id))

