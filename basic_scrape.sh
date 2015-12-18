#!/bin/bash

# Ensure that we're working in the correct directory
cd /var/git/kickscrape

# Run the spider and output results to a json file, logging results to basic_scrape.log
rm -f ./data/project-list.json
/usr/local/bin/scrapy runspider ./basic_spider.py -o ./data/project-list.json -t json 2>&1 | tee -a ./basic_scrape.log
