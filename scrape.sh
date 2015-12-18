#!/bin/bash

# Set the timezone to GMT-6. (Note that POSIX uses positive values
# for west and negative values for east, unlike the ISO standard.)
export TZ="Etc/GMT+6"

# Ensure that we're working in the correct directory
cd /var/git/kickscrape

# Run the spider and output data to a timestamped CSV file. Results are logged in detailscrape.log.
/usr/local/bin/scrapy runspider ./spider.py -o "./data/project-data_$(date +"%Y-%m-%d_%H-%M-%S").csv" -t csv 2>&1 | tee -a scrape.log

