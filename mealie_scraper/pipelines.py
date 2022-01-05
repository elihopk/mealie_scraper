# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import sqlite3

import requests
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DuplicateCheck:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM cachedRecipes WHERE slug=?", adapter.get("slug"))

        if cursor.fetchall():
            conn.close()
            raise DropItem("Duplicate Check: Recipe Already Exists!")

        conn.close()
        return item


class AddItemToMealie:
    def process_item(self, item, spider):
        req = requests.post(
            os.getenv("API_PATH", default="") + "/recipes/create",
            headers={"Authorization": "Bearer " + os.getenv("API_TOKEN")},
            json=dict(item),
        )

        if req.status_code != 200:
            raise DropItem(
                "Add Item to Mealie: Post Request Failed! Status Code: "
                + req.status_code
            )

        return item


class AddItemToCache:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO cachedRecipes (slug) VALUES (?)", adapter.get("slug")
        )

        conn.close()

        return item
