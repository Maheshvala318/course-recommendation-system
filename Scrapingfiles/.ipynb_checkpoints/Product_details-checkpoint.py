from turtledemo.penrose import start

from new_ududemy.items import Product_details
from typing import Iterable
from parsel import Selector
import requests
import re
from new_ududemy.pipelines import NewUdudemyPipeline
import scrapy
from scrapy import Request
from scrapy.cmdline import execute

class ProductDetailsSpider(scrapy.Spider):
    name = "Product_details"
    allowed_domains = ["books.toscrape.com"]

    def __init__(self,start='',end=''):
        self.start=start
        self.end=end
    def start_requests(self) -> Iterable[Request]:
        NewUdudemyPipeline.open_spider(self,"Product_details")
        # self.cursor.execute(f"SELECT * FROM product_link_copy WHERE status='Pending' AND id BETWEEN {self.start} AND {self.end}")

        self.cursor.execute(f"SELECT * FROM product_link_copy where status='Pending'")

        product_details=self.cursor.fetchall()
        for data in product_details:
            print(data)
            res = requests.get(data[1])
            raw={
                'u_id':data[0],
                'course_id': data[2],
                'course_title': data[5],
                'url': data[1],
                'is_paid': data[6],
                'rating': data[7],
                'reviews': data[8],
                'number_of_subscribers': data[9],
                'duration':data[10],
                'level': data[11],
                'sub_category_name': data[3],
                'category_name': data[4],
                'response':res.text
                }

            yield scrapy.Request("https://books.toscrape.com",meta=raw,dont_filter=True)



    def parse(self, response):
        print(response)
        response_html=Selector(response.meta.get('response'))
        tag_keywords=response_html.xpath('//div[contains(@class,"topic-menu topic-menu")]/a/text()').getall()
        price=response_html.xpath('//meta[@property="udemy_com:price"]/@content').get()
        discription=re.sub(r'<[^>]*>','',response_html.xpath('//div[@data-purpose="safely-set-inner-html:description:description"]').get())
        platform="udemy"
        item=Product_details(
        course_id=response.meta.get('course_id'),
        course_title = response.meta.get('course_title'),
        url = response.meta.get('url'),
        price = price,
        is_paid = response.meta.get('is_paid'),
        rating = response.meta.get('rating'),
        reviews = response.meta.get('reviews'),
        number_of_subscribers = response.meta.get('number_of_subscribers'),
        duration = response.meta.get('duration'),
        level = response.meta.get('level'),
        platform = platform,
        tag_keywords =str(tag_keywords).replace('[','').replace(']','').strip(),
        description = discription,
        sub_category_name =response.meta.get('sub_category_name'),
        category_name = response.meta.get('category_name'),
        u_id=response.meta.get('u_id')
        )
        yield item


if __name__ == '__main__':
    execute("scrapy crawl Product_details".split())