"""
Cleaned scraping module: Product Link Spider.

Scrapes individual course links from Udemy's discovery API
for each category/subcategory/topic. Uses MySQL for category data.

Original: Scrapingfiles/product_link.py

NOTE: MySQL credentials loaded from environment variables —
      set MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE in .env
"""

import json
import os
import sys
from pathlib import Path
from typing import Iterable

import pymysql
import requests
import scrapy
from scrapy import Request
from scrapy.cmdline import execute

# Add project root for config imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import MYSQL_DATABASE, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_USER


class ProductLinkSpider(scrapy.Spider):
    """Scrapes course links for each Udemy category/topic."""

    name = "product_link"
    allowed_domains = ["books.toscrape.com"]

    def start_requests(self) -> Iterable[Request]:
        cn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        cursor = cn.cursor()
        cursor.execute("SELECT name, url, c_id FROM category_link")
        all_categories = cursor.fetchall()

        for data in all_categories:
            name = data[0]
            c_id = data[2]
            api_url = (
                f"https://www.udemy.com/api-2.0/discovery-units/all_courses/"
                f"?page_size=16&subcategory_id={c_id}"
                f"&source_page=subcategory_page&locale=en_US"
                f"&skip_price=true&sort=popularity"
            )
            res = requests.get(api_url)
            category_topic = json.loads(res.text)

            topic_list = [
                {"topic_name": t["title"], "topic_id": t["id"]}
                for t in category_topic["unit"]["course_labels"]
            ]

            yield scrapy.Request(
                "https://books.toscrape.com/",
                meta={"category_name": name, "topic_details": topic_list, "id": c_id},
                dont_filter=True,
            )

    def parse(self, response):
        category_name = response.meta.get("category_name")
        c_id = response.meta.get("id")

        for topic in response.meta.get("topic_details"):
            topic_id = topic["topic_id"]
            sub_category_name = topic["topic_name"]

            # Get total pages
            api_url = (
                f"https://www.udemy.com/api-2.0/discovery-units/all_courses/"
                f"?p=1&page_size=16&course_label={topic_id}"
                f"&subcategory_id={c_id}&source_page=subcategory_page"
                f"&locale=en_US&skip_price=true"
            )
            res = requests.get(api_url)
            page_count = json.loads(res.text)["unit"]["pagination"]["total_page"]

            for page_no in range(1, page_count + 1):
                page_url = api_url.replace("p=1", f"p={page_no}")
                page_res = requests.get(page_url)
                if page_res.status_code == 200:
                    yield scrapy.Request(
                        "https://books.toscrape.com/",
                        meta={
                            "page_response": page_res.text,
                            "sub_category_name": sub_category_name,
                            "category_name": category_name,
                        },
                        callback=self.page_link,
                        dont_filter=True,
                    )

    def page_link(self, response):
        page_data = json.loads(response.meta.get("page_response"))
        for course in page_data["unit"]["items"]:
            yield {
                "course_id": course["id"],
                "course_title": course["title"],
                "url": "https://www.udemy.com" + course["url"],
                "sub_category_name": response.meta.get("sub_category_name"),
                "category_name": response.meta.get("category_name"),
                "is_paid": course["is_paid"],
                "rating": course["rating"],
                "reviews": course["num_reviews"],
                "number_of_subscribers": course["num_subscribers"],
                "duration": course["content_info_short"],
                "level": course["instructional_level"],
            }


if __name__ == "__main__":
    execute("scrapy crawl product_link".split())
