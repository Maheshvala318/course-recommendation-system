"""
Cleaned scraping module: Category Link Spider.

Scrapes Udemy category/subcategory URLs from the marketplace API.
This is a reference module — run only when data needs regeneration.

Original: Scrapingfiles/category_link.py
"""

import json
import os

import requests
import scrapy
from scrapy.cmdline import execute


class CategoryLinkSpider(scrapy.Spider):
    """Scrapes all Udemy course categories and subcategories."""

    name = "category_link"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def start_requests(self):
        url = "https://www.udemy.com/frontends-marketplace-experience/api/context/?locale=en"
        udemy_response = requests.get(url)
        if udemy_response.status_code == 200:
            yield scrapy.Request(
                "https://books.toscrape.com/",
                callback=self.parse,
                meta={"udemy_response": udemy_response.text},
            )

    def parse(self, response):
        udemy_page_response = response.meta.get("udemy_response")
        course_category = json.loads(
            udemy_page_response.replace("window.__UDMY_APP_CONTEXT = ", "")
        )
        for category in course_category["header"]["navigationCategories"]:
            for c_name in category["sublist"]["items"]:
                yield {
                    "name": c_name["sd_tag"]["title"],
                    "url": "https://www.udemy.com" + c_name["sd_tag"]["url"],
                    "c_id": c_name["sd_tag"]["id"],
                }


if __name__ == "__main__":
    execute("scrapy crawl category_link".split())
