import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class MyItem(scrapy.Item):
    url = scrapy.Field()


class LinkSpider(scrapy.Spider):
    name = 'linkspider'
    # allowed_domains = ["amazon.in"]
    # start_urls = ["https://www.redbubble.com/shop/?query=usf&ref=search_box"]
    LOG_ENABLED = False
    ret_links = []
    pagecount = 0

    myBaseUrl = ''
    start_urls = []

    def __init__(self, category='', **kwargs):  # The category variable will have the input URL.
        self.myBaseUrl = category
        self.start_urls.clear()
        self.start_urls.append(self.myBaseUrl)
        super().__init__(**kwargs)

    # custom_settings = {'FEED_URI': 'tutorial/outputfile.json', 'CLOSESPIDER_TIMEOUT': 15}

    def parse(self, response):

        image_urls = response.css('img')
        for url in image_urls:
            img_url = url.xpath('@src').get()
            if ".jpg" in img_url:
                if "https:" not in img_url:
                    img_url = "https:"+img_url
                # self.ret_links.append("https:"+img_url)

                yield MyItem(url = img_url)
        if self.pagecount < 5:
            self.pagecount += 1
            next_page = response.xpath('//a[@aria-label="next page"]/@href').get()
            next_url = "https://www.fanatics.com/" + str(next_page)
            print("NEXT PAGE :" + str(next_url))
            yield response.follow(next_url, callback=self.parse)




            # if ".jpg" in img_url:
            #     sub_str = ".jpg"
            #     re = img_url.split(sub_str)
            #     res = "https:" + re[0]+sub_str
            #     self.ret_links.append(res)