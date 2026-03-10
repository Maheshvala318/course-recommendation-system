"""
Cleaned scraping module: Product Details Spider.

Scrapes detailed course information (description, keywords, price)
from individual Udemy course pages.

Original: Scrapingfiles/Product_details.py
"""

import re
import sys
from pathlib import Path
from typing import Iterable

import requests
import scrapy
from parsel import Selector
from scrapy import Request
from scrapy.cmdline import execute

# Add project root for config imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import MYSQL_DATABASE, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_USER


class ProductDetailsSpider(scrapy.Spider):
    """Scrapes full details from individual Udemy course pages."""

    name = "Product_details"
    allowed_domains = ["books.toscrape.com"]

    def start_requests(self) -> Iterable[Request]:
        import pymysql

        cn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = cn.cursor()
        cursor.execute("SELECT * FROM product_link_copy WHERE status='Pending'")
        product_details = cursor.fetchall()

        for data in product_details:
            res = requests.get(data[1])
            raw = {
                "u_id": data[0],
                "course_id": data[2],
                "course_title": data[5],
                "url": data[1],
                "is_paid": data[6],
                "rating": data[7],
                "reviews": data[8],
                "number_of_subscribers": data[9],
                "duration": data[10],
                "level": data[11],
                "sub_category_name": data[3],
                "category_name": data[4],
                "response": res.text,
            }
            yield scrapy.Request(
                "https://books.toscrape.com",
                meta=raw,
                dont_filter=True,
            )

    def parse(self, response):
        response_html = Selector(response.meta.get("response"))

        tag_keywords = response_html.xpath(
            '//div[contains(@class,"topic-menu topic-menu")]/a/text()'
        ).getall()

        price = response_html.xpath(
            '//meta[@property="udemy_com:price"]/@content'
        ).get()

        description_raw = response_html.xpath(
            '//div[@data-purpose="safely-set-inner-html:description:description"]'
        ).get()
        description = re.sub(r"<[^>]*>", "", description_raw) if description_raw else ""

        yield {
            "course_id": response.meta.get("course_id"),
            "course_title": response.meta.get("course_title"),
            "url": response.meta.get("url"),
            "price": price,
            "is_paid": response.meta.get("is_paid"),
            "rating": response.meta.get("rating"),
            "reviews": response.meta.get("reviews"),
            "number_of_subscribers": response.meta.get("number_of_subscribers"),
            "duration": response.meta.get("duration"),
            "level": response.meta.get("level"),
            "platform": "udemy",
            "tag_keywords": str(tag_keywords).replace("[", "").replace("]", "").strip(),
            "description": description,
            "sub_category_name": response.meta.get("sub_category_name"),
            "category_name": response.meta.get("category_name"),
            "u_id": response.meta.get("u_id"),
        }


if __name__ == "__main__":
    execute("scrapy crawl Product_details".split())
