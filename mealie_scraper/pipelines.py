import os
import sqlite3

import requests
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

# Pipeline to Verify this Recipe hasn't been Scraped in a Previous Run
class DuplicateCheck:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Connect to the database
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()

        # TODO: Implement Fuzzy Duplicate Checking
        # Get exact matches for slug.
        cursor.execute("SELECT id FROM cachedRecipes WHERE slug=?", adapter.get("slug"))

        # Check if anything was returned and if so drop the recipe
        if cursor.fetchall():
            conn.close()
            raise DropItem("Duplicate Check: Recipe Already Exists!")

        # Close db connection and continue to next pipeline
        conn.close()
        return item

# Pipeline to Add the Recipe to Mealie
class AddItemToMealie:
    def process_item(self, item, spider):
        # Make request to /recipes/create endpoint with appropriate options
        req = requests.post(
            os.getenv("API_PATH", default="") + "/recipes/create",
            headers={"Authorization": "Bearer " + os.getenv("API_TOKEN")},
            json=dict(item),
        )

        # Check that the request was successful and if not, drop the recipe
        if req.status_code != 200:
            raise DropItem(
                "Add Item to Mealie: Post Request Failed! Status Code: "
                + req.status_code
            )

        # Continue to next pipeline
        return item

# Pipeline to Include Current Recipe in Cache DB
class AddItemToCache:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Open connection with cache DB
        conn = sqlite3.connect("cache.db")
        cursor = conn.cursor()

        # Insert the current recipe
        cursor.execute(
            "INSERT INTO cachedRecipes (slug) VALUES (?)", adapter.get("slug")
        )

        # Close DB connection
        conn.close()

        # This is the last item pipeline
        return item
