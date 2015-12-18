import scrapy, re
from datetime import datetime

class KickStatsItem(scrapy.Item):
    name       = scrapy.Field()
    url        = scrapy.Field()
    status     = scrapy.Field()

class KickSpider(scrapy.Spider):
    name = 'kickspider'
    allowed_domains = ['kicktraq.com']
    start_urls = ['http://www.kicktraq.com/search/?find=in:"video+games"&sort=new']
    custom_settings = { 'DEPTH_LIMIT': 50 }

    def parse(self, response):
        projects = response.css('#project-list > .projects > .project')
        
        # Parse the projects
        for project in projects:
            name = project.css('.project-infobox > h2 > a::text')[0].extract()
            url  = project.css('.project-infobox > h2 > a::attr("href")')[0].extract()
            url  = response.urljoin(url)
            url  = url.replace('www.kicktraq.com', 'www.kickstarter.com')
            status = project.css('.project-infobox > .project-infobits .project-pledgilizer-top > h5::text')[0].extract()
            status = status.lower()

            # Differentiate between success and failure
            if status == 'closed':
                percent = project.css('.project-infobox > .project-infobits .project-pledgilizer-mid > h4::text')[0].extract()
                percent = int(percent[:-1])
                
                if percent >= 100:
                    status = 'success'
                else:
                    status = 'failure'

            # Construct item
            item = KickStatsItem()
            item['name']       = name
            item['url']        = url
            item['status']     = status

            yield item

	# Crawl the next page
        next_page = response.css('#project-list .paging a:last-of-type::attr("href")')

        if next_page:
            url = response.urljoin(next_page[0].extract()) + '&sort=new' # Need to enforce sort
            yield scrapy.Request(url)

