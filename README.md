CMPS 140 Artwork Classifier
==========================

This project is an artwork classifier based on [this dataset](https://www.kaggle.com/metmuseum/the-metropolitan-museum-of-art-open-access/data) from the Met.

Getting started
================

 * Download the above file and place `MetObjects.csv` in this directory.
 * Install numpy, pandas, jupyter, etc.
 * Run `jupyter notebook` in this directory and open `ArtworkClassifier.ipynb`

Running the scraper
=================

 * Ideally run within a virtualenv
 * Requires Python 3.6
 * If the crawler throws an error like `FileNotFoundError: [Errno 2] No such file or directory: 'images/32.jpg'`, manually create an `images` directory under `scraper`.
 * Run `python3 met-scraper.py`
