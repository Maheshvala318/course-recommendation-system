import json
from typing import Iterable
from new_ududemy.items import Product_link
import requests
from new_ududemy.pipelines import NewUdudemyPipeline
import scrapy
from scrapy import Request
from scrapy.cmdline import execute
import pymysql

class ProductLinkSpider(scrapy.Spider):
    name = "product_link"
    allowed_domains = ["books.toscrape.com"]
    def __init__(self,start='',end=''):
        self.start=start
        self.end=end
    def start_requests(self) -> Iterable[Request]:
        cn=pymysql.connect(host="localhost", user="root", password="Lost@123", database="new_udamy")
        cursor =cn.cursor()
        # cursor.execute(f"SELECT name,url,c_id FROM category_link where id BETWEEN {self.start} AND {self.end}")
        cursor.execute(f"SELECT name,url,c_id FROM category_link")

        all_categories=cursor.fetchall()
        # print(all_categories)
        for data in all_categories:
            name=data[0]
            link=data[1]
            id=data[2]
            new_url=f"https://www.udemy.com/api-2.0/discovery-units/all_courses/?page_size=16&subcategory=&instructional_level=&lang=&price=&duration=&closed_captions=&subs_filter_type=&sort=popularity&subcategory_id={id}&source_page=subcategory_page&locale=en_US&navigation_locale=en&skip_price=true&sos=ps&fl=scat"
            print("______________")
            res=requests.get(new_url)
            print("aaaaaaaaaaaa")
            # print(res.status_code)
            category_topic=json.loads(res.text)
            topic_list=[]
            # print(category_topic)
            for topic_dic in category_topic['unit']['course_labels']:
                topic_list.append({
                    "topic_name":topic_dic['title'],
                    "topic_id":topic_dic['id']
                })
                # print(topic_dic)
            yield scrapy.Request("https://books.toscrape.com/",meta={"category_name":name,"topic_details":topic_list,"id":id},dont_filter=True)





    def parse(self, response):
        category_name =response.meta.get("category_name")
        # print(category_name)
        c_id=response.meta.get('id')
        for l in response.meta.get("topic_details"):
            p=1
            sub_category_name=l["topic_name"]
            new_url = f'https://www.udemy.com/api-2.0/discovery-units/all_courses/?p={p}&page_size=16&subcategory=&instructional_level=&lang=&price=&duration=&closed_captions=&subs_filter_type=&course_label={l["topic_id"]}&subcategory_id={c_id}&source_page=subcategory_page&locale=en_US&navigation_locale=en&skip_price=true&sos=ps&fl=scat'
            new_response = requests.get(new_url)
            json_dict=json.loads(new_response.text)
            pge_cnt=json_dict['unit']['pagination']['total_page']
            for no in range(1,pge_cnt+1):
                new_url1=f'https://www.udemy.com/api-2.0/discovery-units/all_courses/?p={no}&page_size=16&subcategory=&instructional_level=&lang=&price=&duration=&closed_captions=&subs_filter_type=&course_label={l["topic_id"]}&subcategory_id={c_id}&source_page=subcategory_page&locale=en_US&navigation_locale=en&skip_price=true&sos=ps&fl=scat'
                new_response1 = requests.get(new_url1)
                raw = {
                    "page_response": new_response1.text,
                    "sub_category_name": sub_category_name,
                    "category_name": category_name
                }
                # print("raw:",raw)
                if new_response.status_code==200:
                    print(new_response.text)
                    yield scrapy.Request("https://books.toscrape.com/",meta=raw,callback=self.page_link,dont_filter=True)




        # print(len(response.meta.get("topic_details")))
    def page_link(self,response):
        page_json_data=response.meta.get('page_response')
        page_data_dic=json.loads(page_json_data)
        print(page_json_data)
        for course in page_data_dic['unit']['items']:
            id=course['id']
            course_title=course['title']
            url=course['url']
            sub_category_name=response.meta.get('sub_category_name')
            category_name=response.meta.get('category_name')
            is_paid=course['is_paid']
            rating=course['rating']
            reviews=course['num_reviews']
            number_of_subscribers=course['num_subscribers']
            duration=course['content_info_short']
            level=course['instructional_level']
            item = Product_link(
                course_title=course_title,
                course_id=id,
                url="https://www.udemy.com"+url,
                sub_category_name=sub_category_name,
                category_name=category_name,
                is_paid=is_paid,
                rating=rating,
                reviews=reviews,
                number_of_subscribers=number_of_subscribers,
                duration=duration,
                level=level
            )
            yield item






if __name__ == '__main__':
    execute("scrapy crawl product_link".split())