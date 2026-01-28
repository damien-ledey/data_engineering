import scrapy


class SteamSearchSpiderSpider(scrapy.Spider):
    name = "steam_search_spider"
    allowed_domains = ["store.steampowered.com"]
    start_urls = ["https://store.steampowered.com/search?term=&page=1&count=100"]
    current_page = 1

    def parse(self, response):
        for cit in response.xpath('//a[contains(@class, "search_result_row")]'):
            id_value = cit.xpath('.//@data-ds-appid').get()
            title_value = clean_spaces(cit.xpath('.//span[@class="title"]/text()').get())
            thumbnail_link = cit.xpath('.//div[@class="search_capsule"]/img/@src').get()
            release_value = clean_spaces(cit.xpath('.//div[@class="search_released responsive_secondrow"]/text()').get())
            review_value = clean_spaces(cit.xpath('.//div[@class="search_reviewscore responsive_secondrow"]/span/@data-tooltip-html').get())

            # Clean review_value
            if review_value is not None:
                review_text = review_value.split("<br>")[0].strip()
                review_score = review_value.split("<br>")[1].split(" ")[0].strip()[0:-1]
                review_total = review_value.split("<br>")[1].split(" ")[3].strip()
            else:
                review_text = "No reviews"
                review_score = "N/A"
                review_total = "0"

            price_value = clean_spaces(cit.xpath('.//div[@class="discount_final_price"]/text()').get())


            hover_url = f"https://store.steampowered.com/apphoverpublic/{id_value}?review_score_preference=0&l=french&ls[]=french&origin=https://store.steampowered.com&pagev6=true"

            if price_value is None:
                price_value = "Gratuit"

            yield scrapy.Request(url=hover_url, callback=self.parse_hover, meta={'app_id': id_value, 'title': title_value, 'thumbnail_link': thumbnail_link, 'release': release_value, 'review_text': review_text, 'review_score': review_score, 'review_total': review_total, 'price': price_value})
        
        # Pagination
        self.current_page += 1

        if self.current_page > 1:
            return

        next_page_url = f"https://store.steampowered.com/search?term=&page={self.current_page}&count=100"
        yield scrapy.Request(url=next_page_url, callback=self.parse)

    def parse_hover(self, response):
        app_id = response.meta['app_id']
        title = response.meta['title']
        release = response.meta['release']
        price = response.meta['price']
        thumbnail_link = response.meta['thumbnail_link']
        review_text = response.meta['review_text']
        review_score = response.meta['review_score']
        review_total = response.meta['review_total']

        tags = []
        for tag in response.xpath('.//div[@class="app_tag"]/text()'):
            tags.append(clean_spaces(tag.get()))
        print(tags)

        yield {'app_id': app_id, 'title': title, 'thumbnail_link': thumbnail_link, 'release': release, 'review_text': review_text, 'review_score': review_score, 'review_total': review_total, 'price': price, 'tags': tags}

def clean_spaces(string_):
    if string_ is not None:
        return " ".join(string_.split())