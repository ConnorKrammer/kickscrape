KickScrape
==========

A Kickstarter data-scraper project.

About
-----

This project scrapes crowdfunding data from Kickstarter to allow detailed analysis.
Because Kickstarter hides failed, cancelled, or suspended projects from its search
results and discover interface, a collection of projects is first retrieved from
Kicktraq.com.  Kicktraq is a crowdfunding analytics and discovery platform, and
tracks projects that are launched on Kickstarter, even after they fail. The project
list scraped from Kicktraq can be found under `data/project-list.json`.

Once a list of projects is gathered from Kicktraq, a second scraper is deployed to
collect detailed data from individual projects on Kickstarter proper. Each project
has over 30 datapoints which are gathered and stored in JSON and CSV format. While
the data from Kicktraq yields about 750 projects to analyze, only successful or failed
projects are scraped in this second step. Active, cancelled and suspended projects
are ignored; only projects that have completed their full crowdfunding term are
considered. Successful and failed projects are both handled differently due to their
different HTML structures on Kickstarter's website, but the same data points are
collected in both cases. (Notably, successful projects require one additional HTTP
request—3, instead of 2—because less information is displayed on the main project
page.) The results of the scraper are written to a CSV file at the filepath
`data/project-data.csv`. This file is also duplicated in JSON format to provide a
more human-readable format, and to allow a wider range of programming library choices
when analyzing the data later.

Data Points Collected
---------------------

Individual data points:
 - `backer_count`         => The number of campaign backers
 - `comment_count`        => The number of campaign comments
 - `creator_num_backed`   => The number of other campaigns backed by the project creators
 - `creator_num_created`  => The number of campaigns created by the project creator
 - `description_length`   => The number of characters in the campaign description
 - `description_images`   => The number of images in the campaign description
 - `description_links`    => The number of hyperlinks in the campaign description
 - `funding_currency`     => The ISO 4217 code for the campaign collection currency
 - `funding_goal`         => The funding goal of the campaign
 - `funding_raised`       => The amount of funds raised by the end of the campaign
 - `funding_percent`      => The percent of desired funds raised
 - `tier_count`           => The number of unique tiers for backers to pledge at
 - `tier_limits`          => The max number of slots for each tier, or "False" if no limit (comma-separated)
 - `tier_limited_count`   => The number of limited tiers
 - `tier_text_length`     => The number of characters in each tier description (comma-separated)
 - `tier_values`          => The currency value of each tier (comma-separated)
 - `tier_backers`         => The number of backers of each tier (comma-separated)
 - `tier_text_length_avg` => The average number of characters for all tier descriptions
 - `tier_values_avg`      => The average currency value for all tiers
 - `tier_backers_avg`     => The average number of backers per tier 
 - `project_name`         => The campaign title
 - `project_url`          => The project URL
 - `project_start`        => An ISO 8601 datetime stamp for the moment the project started
 - `project_end`          => An ISO 8601 datetime stamp for the moment the project ended
 - `project_duration`     => The number of days in the campaign's duration 
 - `project_status`       => Whether the project successed for failed ("success" || "failure")
 - `project_video`        => Whether the project had a video on its main page ("True" || "False")
 - `update_count`         => The number of creator-posted updates made while the campaign was running
 - `update_comments`      => The number of user comments on each update (comma-separated)
 - `update_likes`         => The number of user "likes" on each update (comma-separated)
 - `update_times`         => The ISO 8601 datetime stamp for the moment each update was posted (comma-separated)
 - `update_comments_avg`  => The average number of user comments posted on each update
 - `update_likes_avg`     => The average number of user "likes" made on each update
 - `update_times_avg`     => The average time of day updates were posted at (decimal hours since midnight)

Total: 34

**Notes**:
 - All "update" variables take on values of "False" when the variable `update_count` is
   equal to zero.
 - Because of the excessive number of HTTP requests required to filter through backer
   comments, there is no distinction made between comments posted during and comments
   posted after the campaign's close. Because the projects scraped are all relatively
   recent, this should not be too much of an issue. However, it will inflate the number
   of comments for older campaigns relative to new ones.
 - Because the campaign description is locked to edits when a campaign ends, the description
   stats are accurate for that time. However, they don't capture the significance of any
   changes that may have occurred over the course of the campaign.
 - Campaign managers will on occassion re-issue limited-quantity tiers to backers by creating
   an entirely new tier with the same details as before. These "duplicate" tiers are not
   handled any differently.
 - While relevant, it is not possible to capture the effects of shipping costs (which are added
   on to the price of each tier) or "add-ons" (which are bonus rewards that can be received by
   adding on an additional amount to your pledge without changing tiers). The first could be
   handled if the campaign were scraped while live, using a more sophisticated JavaScript method.
   The second is effectively impossible to collect, as they are not an official Kickstarter feature
   and therefore are not integrated into the UI (and by extension, the HTML).
 - It would be possible to collect social media information by utilizing Twitter's API, but that
   was out of the scope of this project and would be too resource-intensive to ethically carry out
   except in small pieces over a more extended period of time.

Requirements
------------

The following will need to be installed on your computer to run the scripts in
this project without erros:
 - Python 2.7.x
 - Scrapy 1.0.3
 - csvkit 0.9.1
 - html2text 2015.11.4

A Unix operating system will also be required to run the included bash scripts,
though porting them to Windows batch would be fairly trivial.

Project Notes
-------------

This project was designed and tested in a manner that applied miminum load to both
the Kicktraq and Kickstarter websites. At no point was there a danger that the scraper's
requests would affect the site for other users, or cause undue strain upon company
servers.

