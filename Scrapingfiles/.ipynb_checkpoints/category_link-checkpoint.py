import json

import scrapy
import requests
from scrapy.cmdline import execute
from new_ududemy.items import UdemyItem
class CategoryLinkSpider(scrapy.Spider):
    name = "category_link"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def start_requests(self):
        url="https://www.udemy.com/frontends-marketplace-experience/api/context/?locale=en"
        udemy_response=requests.get(url)
        if udemy_response.status_code == 200:
            yield scrapy.Request("https://books.toscrape.com/", callback=self.parse,
                                 meta={"udemy_response": udemy_response.text})

    def parse(self, response):
        udemy_page_response=response.meta.get("udemy_response")
        # print(udemy_page_response.replace('window.__UDMY_APP_CONTEXT = ',''))
        course_category=json.loads(udemy_page_response.replace('window.__UDMY_APP_CONTEXT = ',''))
        for category in course_category['header']['navigationCategories']:
            print(category)
            for c_name in category['sublist']['items']:
                item = UdemyItem(
                        name=c_name['sd_tag']['title'],
                        url="https://www.udemy.com"+c_name['sd_tag']['url'],
                        c_id=c_name['sd_tag']['id']
                    )
                yield item









if __name__ == '__main__':
    execute("scrapy crawl category_link".split())
