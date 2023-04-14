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

    myBaseUrl = ''
    start_urls = []

    def __init__(self, category='', **kwargs):  # The category variable will have the input URL.
        self.myBaseUrl = category
        self.start_urls.append(self.myBaseUrl)
        super().__init__(**kwargs)

    custom_settings = {'FEED_URI': 'tutorial/outputfile.json', 'CLOSESPIDER_TIMEOUT': 15}

    def parse(self, response):

        image_urls = response.css('img')
        for url in image_urls:
            img_url = url.xpath('@src').get()
            if img_url.endswith(".jpg"):
                self.ret_links.append(img_url)
                print("GOT ONE !!!!!!")
                yield MyItem(url = img_url)




            # if ".jpg" in img_url:
            #     sub_str = ".jpg"
            #     re = img_url.split(sub_str)
            #     res = "https:" + re[0]+sub_str
            #     self.ret_links.append(res)