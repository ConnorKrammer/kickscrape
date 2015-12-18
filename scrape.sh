#!/bin/bash

# Ensure that we're working in the correct directory
cd /var/git/kickscrape

# Run the spider and output data to a CSV file, logging results to scrape.log
rm -f ./data/project-data_*
/usr/local/bin/scrapy runspider ./spider.py -o ./data/project-data.csv -t csv 2>&1 | tee -a ./scrape.log

# Make a JSON duplicate of the data, for readability purposes
csvjson -i 4 ./data/project-data.csv 2>&1 | tee -a ./data/project-data.json

