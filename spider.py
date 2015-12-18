from __future__ import division
import scrapy, re, json, html2text

# Fields ordered alphabetically by first word
class KickStatsItem(scrapy.Item):
    backer_count         = scrapy.Field() # int (backers)
    comment_count        = scrapy.Field() # int (comments)
    creator_num_comments = scrapy.Field() # int (comments)
    creator_num_backed   = scrapy.Field() # int (projects)
    creator_num_cancel   = scrapy.Field() # int (projects)
    creator_num_created  = scrapy.Field() # int (projects)
    creator_num_failed   = scrapy.Field() # int (projects)
    creator_num_success  = scrapy.Field() # int (projects)
    date_end             = scrapy.Field() # ISO 8601 datetime
    date_start           = scrapy.Field() # ISO 8601 datetime
    description_length   = scrapy.Field() # int (characters)
    description_images   = scrapy.Field() # int (images)
    description_links    = scrapy.Field() # int (links)
    duration             = scrapy.Field() # int (days)
    funding_currency     = scrapy.Field() # ISO 4217 currency code
    funding_goal         = scrapy.Field() # int (currency)
    funding_raised       = scrapy.Field() # int (currency)
    funding_percent      = scrapy.Field() # float (percent)
    tier_count           = scrapy.Field() # int (tiers)
    tier_text_length     = scrapy.Field() # comma-separated int list (characters/tier)
    tier_values          = scrapy.Field() # comma-separated int list (currency/tier)
    tier_backers         = scrapy.Field() # comma-separated int list (backers/tier)
    tier_text_length_avg = scrapy.Field() # float (characters)
    tier_values_avg      = scrapy.Field() # float (currency)
    tier_backers_avg     = scrapy.Field() # float (backers)
    project_name         = scrapy.Field() # string
    project_url          = scrapy.Field() # url string
    project_status       = scrapy.Field() # "success" || "failure"
    project_video        = scrapy.Field() # boolean
    update_count         = scrapy.Field() # int (updates)
    update_comments      = scrapy.Field() # False || comma-separated int list (comments/update)
    update_likes         = scrapy.Field() # False || comma-separated int list (likes/update)
    update_times         = scrapy.Field() # False || comma-separated ISO 8601 datetime list (datetime/update)
    update_comments_avg  = scrapy.Field() # False || float (comments)
    update_likes_avg     = scrapy.Field() # False || float (likes)
    update_times_avg     = scrapy.Field() # False || float (hours since midnight)

class KickSpider(scrapy.Spider):
    name = 'kickspider'
    allowed_domains = ['kickstarter.com']

    # Fetches URLS to crawl from the project list compiled by the basic Kicktraq spider
    def start_requests(self):
        request_list = []

        with open('./data/project-list.json') as f:
            project_list = json.load(f)

        for project in project_list:
            status = project['status']
            url = project['url']

            if status not in ['success', 'failure']:
                continue

            url = url.replace('http://', 'https://') # Avoid redirects

            request = scrapy.Request(url + 'description', meta = { 'status': status, 'url': url })
            request_list.append(request)

        return request_list

    def parse(self, response):
        status = response.meta['status']

        # Check if Kickstarter took down the project.
        # This can happen for IP violations or TOS violations, for example.
        if response.css('#hidden_project') or response.css('#purged_project'):
            return

        # Get project name
        if status == 'success':
            project_name = response.css('.project-profile__content .NS_project_profile__title .hero__link::text').extract_first()
        elif status == 'failure':
            project_name = response.css('.NS_projects__header h2 a::text').extract_first()

        # Get funding info
        if status == 'success':
            funding_info   = response.css('.row > .col-right.col-4.py2.border-left .money::text').extract()
            funding_raised = int(re.sub(r'\D', '', funding_info[0]))
            funding_goal   = int(re.sub(r'\D', '', funding_info[1]))
        elif status == 'failure':
            funding_raised = int(float(response.css('#pledged::attr("data-pledged")').extract_first()))
            funding_goal   = int(float(response.css('#pledged::attr("data-goal")').extract_first()))

        funding_percent  = funding_raised / funding_goal * 100

        # Parse 3-letter currency code out of class name
        if status == 'success':
            selector = '.row > .col-right.col-4.py2.border-left .mb1 .money'
        elif status == 'failure':
            selector = '#stats > .row > .col:nth-child(2) > span:first-of-type > .money'
        funding_currency = response.css(selector).re(r'class="money ([\w]+) [\w-]+"')[0]

        # Get comment and backer counts
        # Note: comment count does not exclude comments made after project conclusion
        comment_count = int(response.css('#comments_count::attr("data-comments-count")').extract_first())

        if status == 'success':
            backer_count = response.css('.NS_projects__spotlight_stats > b:first-child::text').extract_first()
            backer_count = int(re.sub('\D', '', backer_count))
        elif status == 'failure':
            backer_count = int(response.css('#backers_count::attr("data-backers-count")').extract_first())

        # Get description stats
        description_html = ''.join(response.css('.full-description').extract())
        description_text = html2text.html2text(description_html)      # Markdown format
        description_length = len(re.sub(r'\W', '', description_text)) # Count, excluding non-word characters
        description_links  = description_html.count('<a')
        description_images = description_html.count('<img')

        # Check for video
        if status == 'success':
            project_video = response.css('.project-image::attr("data-has-video")').extract_first() == "true"
        elif status == 'failure':
            project_video = response.css('#video-section::attr("data-has-video")').extract_first() == "true"

        # Get tier stats
        tier_list = response.css('.NS_projects__rewards_list > ol > li')
        tier_count = len(tier_list)

        tier_values = []
        tier_backers = []
        tier_text_length = []

        for tier in tier_list:
            value = ''.join(tier.css('.pledge__amount::text').extract())
            value = int(re.sub('\D', '', value))
            tier_values.append(value)

            backers = ''.join(tier.css('.pledge__backer-count::text').extract())
            backers = int(re.sub('\D', '', backers))
            tier_backers.append(backers)

            tier_html = ''.join(tier.css('.pledge__info').extract())
            tier_text = html2text.html2text(tier_html)      # Markdown format
            tier_length = len(re.sub(r'\W', '', tier_text)) # Count, excluding non-word characters
            tier_text_length.append(tier_length)

        # Averages
        tier_values_avg      = sum(tier_values) / tier_count
        tier_backers_avg     = sum(tier_backers) / tier_count
        tier_text_length_avg = sum(tier_text_length) / tier_count

        # String list format, to be parsed out again later
        tier_values      = ','.join(str(x) for x in tier_values)
        tier_backers     = ','.join(str(x) for x in tier_backers)
        tier_text_length = ','.join(str(x) for x in tier_text_length)

        # Assign all values to item
        item = KickStatsItem()
        item['project_name']         = project_name
        item['project_url']          = response.meta['url']
        item['funding_raised']       = funding_raised
        item['funding_goal']         = funding_goal
        item['funding_currency']     = funding_currency
        item['funding_percent']      = funding_percent
        item['comment_count']        = comment_count
        item['backer_count']         = backer_count
        item['description_length']   = description_length
        item['description_links']    = description_links
        item['description_images']   = description_images
        item['project_video']        = project_video
        item['tier_count']           = tier_count
        item['tier_values']          = tier_values
        item['tier_backers']         = tier_backers
        item['tier_values_avg']      = tier_values_avg
        item['tier_backers_avg']     = tier_backers_avg
        item['tier_text_length']     = tier_text_length
        item['tier_text_length_avg'] = tier_text_length_avg

        # If failure, get creator stats from front page (not possible on successful projects)
        # Saves an http request and removes parse_creator from the request chain
        if status == 'failure':
            creator_info = response.css('.NS_projects__creator .col:nth-child(2) .flag-body .h5 > span :first-child::text').extract()
            creator_num_created = int(re.sub(r'\D', '', creator_info[0]) or 1)
            creator_num_backed  = int(re.sub(r'\D', '', creator_info[1]))

            item['creator_num_created'] = creator_num_created
            item['creator_num_backed']  = creator_num_backed

        # Now we start chaining requests to other pages, passing along the same results item each time
        # Chain order: parse_updates > parse_creator
        next_url = response.css('#updates_nav::attr("href")').extract_first()
        next_url = response.urljoin(next_url)

        request = scrapy.Request(next_url, callback=self.parse_updates, meta = {
            'item': item,
            'status': status,
            'url': response.meta['url']
        })

        return [request]

    def parse_updates(self, response):
        item = response.meta['item']
        status = response.meta['status']

        # Get end and start date
        update_feed_start = response.css('.timeline .timeline__divider--launched')
        update_feed_end   = response.css('.timeline .timeline__divider:not(.timeline__divider--month)')
        date_end   = update_feed_end.css('time::attr("datetime")').extract_first()
        date_start = update_feed_start.css('time::attr("datetime")').extract_first()

        # Get update information
        timeline_items = response.css('.timeline > *:not(.timeline__divider--month)')
        past_divider = False
        update_list = []

        for t_item in timeline_items:
            if not past_divider and t_item.css('.timeline__divider'):
                past_divider = True
            elif past_divider and t_item.css('.timeline__item'):
                update_list.append(t_item)

        update_list.reverse() # Put it in chronological order

        update_times = []
        update_comments = []
        update_likes = []

        for update in update_list:
            update_metadata = update.css('.grid-post__metadata span')
            update_time = update.css('time::attr("datetime")').extract_first()

            # Complicated but concise. If the regex returns [], inner value becomes [0]. The
            # first value in the list (0) is then passed to int(), resulting in a default of 0.
            update_comments_count = int((update_metadata.re(r'([\d]+) Comments') or [0])[0])
            update_likes_count    = int((update_metadata.re(r'([\d]+) Like') or [0])[0])

            update_times.append(update_time)
            update_comments.append(update_comments_count)
            update_likes.append(update_likes_count)

        update_count = len(update_times)

        # If there were no updates, use False to indicate not applicable
        if update_count != 0:
            update_times_hm = [re.search(r'.+([0-2]\d:[0-5]\d).+', x).group(1) for x in update_times]
            update_times_hm = [x.split(':') for x in update_times_hm]
            update_times_hm = [int(x[0]) + (int(x[1]) / 60) for x in update_times_hm]
            update_times_avg = sum(update_times_hm) / update_count # In hours

            update_comments_avg = sum(update_comments) / update_count
            update_likes_avg = sum(update_likes) / update_count

            # String list format, to be parsed out again later
            update_times    = ','.join(str(x) for x  in update_times)
            update_comments = ','.join(str(x) for x  in update_comments)
            update_likes    = ','.join(str(x) for x  in update_likes)
        else:
            update_comments     = False
            update_comments_avg = False
            update_likes        = False
            update_likes_avg    = False
            update_times        = False
            update_times_avg    = False

        # Store values to pass along
        item['date_start']          = date_start
        item['date_end']            = date_end
        item['update_count']        = update_count
        item['update_comments']     = update_comments
        item['update_comments_avg'] = update_comments_avg
        item['update_likes']        = update_likes
        item['update_likes_avg']    = update_likes_avg
        item['update_times_avg']    = update_times_avg
        item['update_times']        = update_times

        # If creator info has already been grabbed, we can exit early
        if 'creator_num_created' in item and 'creator_num_backed' in item:
            return item

        # Parse the creator's page next
        # We construct the profule URL by manipulating the project URL
        next_url = response.meta['url'].split('/')[:-2]
        next_url[-2] = 'profile'
        next_url = '/'.join(next_url)

        request = scrapy.Request(next_url, callback=self.parse_creator, meta = {
            'item': item,
            'status': status,
            'url': response.meta['url']
        })

        return [request]

    def parse_creator(self, response):
        item = response.meta['item']

        creator_num_backed  = int(response.css('#project_nav > li:first-child .count::text').extract_first())
        creator_num_created = int(response.css('#project_nav > li:nth-child(2) .count::text').extract_first())

        item['creator_num_created'] = creator_num_created
        item['creator_num_backed']  = creator_num_backed
        
        return item

