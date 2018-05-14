import numpy as np
import pandas as pd

import os
import random

"""
This script moves previously-scraped images into a new folder if they match
our criteria to be included in analysis later (>1000 samples per Object Name).
Basically, we only want to scrape images for an Object Name (painting, vase, etc.)
if we have more than 1000 examples of them in the dataset. This script lets us avoid
re-scraping old images.
"""

DATASET_PATH = 'MetObjects.csv'
NEW_PATH = 'images'
OLD_PATH = 'old-images'
MAX_RETRIES = 3
BUCKET_THRESHOLD = 1000


def get_relevant_data() -> pd.core.frame.DataFrame:
    df = pd.read_csv(DATASET_PATH)
    public_domain = df.loc[df['Is Public Domain'] == True]
    artwork = public_domain.groupby('Object Name').filter(lambda x: len(x) >= BUCKET_THRESHOLD)
    # TODO: additionally filter by only the top 10 buckets
    # TODO: remove hard-coded id of last downloaded image
    return artwork.loc[:100888]

def get_training_testing_data() -> (dict, dict):
    artwork = get_relevant_data()
    classes = artwork['Object Name']
    # get the top 10 classes
    top_10_labels = classes.value_counts()[:10]
    # convert from an Index to a list (https://stackoverflow.com/a/41456363/1221477)
    top_10_labels = top_10_labels.axes[0].tolist()
    training = {}
    testing = {}
    for label in top_10_labels:
        # get downloaded images matching this class
        downloaded_imgs = artwork.loc[artwork['Object Name'] == label]
        downloaded_imgs_indexes = downloaded_imgs.index.tolist()
        random.shuffle(downloaded_imgs_indexes)
        num_imgs = len(downloaded_imgs_indexes)
        if len(downloaded_imgs_indexes) >= 1000:
            num_imgs = 1000
        training_set_size = int(0.9 * num_imgs)
        sampled_downloaded_imgs_indexes = downloaded_imgs_indexes[:num_imgs]
        training[label] = sampled_downloaded_imgs_indexes[:training_set_size]
        testing[label] = sampled_downloaded_imgs_indexes[training_set_size:num_imgs]
    return training, testing


def bucket_images():
    training, testing = get_training_testing_data()
    bucket_images_by_label("training", training)
    bucket_images_by_label("testing", testing)

def bucket_images_by_label(data_type, dataset):
    if data_type not in ("training", "testing"):
        raise Exception("Invalid data type: {}".format(data_type))

    f = open('bucketing_errors.txt', 'w')

    for label, img_ids in dataset.items():
        # create a directory for these labelled images if it doesn't exist
        label_dir = "{}/{}".format(data_type, label)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)
        for img_id in img_ids:
            new_path = "{}/{}.jpg".format(label_dir, img_id)
            old_path = "images/{}.jpg".format(img_id)
            if not os.path.isfile(old_path):
                f.write("{}\n".format(old_path))
                continue
            os.rename(old_path, new_path)
    f.close()


def move_relevant_images_to_own_directory():
    buckets = get_relevant_data()
    public_domain_links = buckets['Link Resource']
    for artwork_id, page_url in public_domain_links.iteritems():
        old_image_path = "{}/{}.jpg".format(OLD_PATH, artwork_id)
        new_image_path = "{}/{}.jpg".format(NEW_PATH, artwork_id)
        if os.path.isfile(old_image_path):
            os.rename(old_image_path, new_image_path)
            print("Moved {}".format(artwork_id))


if __name__ == "__main__":
    print("Please import this script as a module and call the relevant functions.")
