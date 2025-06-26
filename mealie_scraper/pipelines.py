import json
import os
import re
import sqlite3
from html import unescape

import requests
import unidecode
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


# Pipeline to Unescape HTML Characters and Ensure Text is Properly Formatted
class UnescapeHTML:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        adapter["name"] = unescape(adapter.get("name"))

        if adapter.get("description"):
            adapter["description"] = unescape(adapter.get("description"))

        if isinstance(adapter.get("recipeCategory"), list):
            for i, cat in enumerate(adapter.get("recipeCategory")):
                adapter["recipeCategory"][i] = unescape(cat)
        elif adapter.get("recipeCategory"):
            adapter["recipeCategory"] = unescape(adapter.get("recipeCategory"))

        if adapter.get("recipeIngredient"):
            for i, ingredient in enumerate(adapter.get("recipeIngredient")):
                adapter["recipeIngredient"][i]["title"] = unescape(ingredient["title"])

        if adapter.get("recipeInstructions"):
            for i, instruction in enumerate(adapter.get("recipeInstructions")):
                adapter["recipeInstructions"][i]["text"] = unescape(instruction["text"])

        return item


# Pipeline to Convert the Recipe Name into a Slug and Save
class AddSlug:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        adapter["slug"] = adapter.get("name").strip()
        adapter["slug"] = adapter.get("slug").lower()
        adapter["slug"] = adapter.get("slug").replace(" ", "-")
        adapter["slug"] = unidecode.unidecode(adapter.get("slug"))
        adapter["slug"] = re.sub(r"[^a-zA-Z0-9-]", "", adapter.get("slug"))

        lastchar = ""
        newslug = ""

        # Remove Repeating Hyphens
        for char in adapter.get("slug"):
            if char == "-" and lastchar == "-":
                continue

            newslug += char
            lastchar = char

        adapter["slug"] = newslug

        return item


# Pipeline to Verify this Recipe hasn't been Scraped in a Previous Run
class DuplicateCheck:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Connect to the database
        conn = sqlite3.connect("/usr/src/app/mealie_scraper/cache.db")
        cursor = conn.cursor()

        # TODO: Implement Fuzzy Duplicate Checking
        # Get exact matches for slug.
        cursor.execute(
            "SELECT slug FROM cachedRecipes WHERE slug=?", (adapter.get("slug"),)
        )

        # Check if anything was returned and if so drop the recipe
        if cursor.fetchall():
            conn.close()
            raise DropItem("Duplicate Check: Recipe Already Exists!")

        # Close db connection and continue to next pipeline
        cursor.close()
        conn.close()
        return item

class ParseIngredients:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        recipeIngredient = adapter.get("recipeIngredient")
        newRecipeIngredients = []

        # Parse the ingredients to ensure they are in the correct format
        if isinstance(recipeIngredient, list):
            for ingredient in recipeIngredient:
                if isinstance(ingredient, dict):
                    for value in ingredient.values():
                        if isinstance(value, str):
                            newRecipeIngredients.append(value)
                        else:
                            raise DropItem(
                                "recipeIngredient must be a list of strings or dictionaries with string values."
                            )
                elif isinstance(ingredient, str):
                    newRecipeIngredients.append(ingredient)
        else:
            raise DropItem("recipeIngredient must be a list of ingredients.")

        adapter["recipeIngredient"] = newRecipeIngredients

        return item 

# Pipeline to Add the Recipe to Mealie
class AddItemToMealie:
    def process_item(self, item, spider):
        item_temp = dict(item)

        item_temp["@context"] = "https://schema.org"
        item_temp["@type"] = "Recipe"

        # Make request to /recipes/create endpoint with appropriate options
        req = requests.post(
            os.getenv("API_PATH", default="") + "/recipes/create/html-or-json",
            headers={"Authorization": "Bearer " + os.getenv("API_TOKEN")},
            json={
                "includeTags": False,
                "data": json.dumps(item_temp),
            },
        )

        # Check that the request was successful and if not, drop the recipe
        if req.status_code != 201:
            try:
                raise DropItem(
                    "Add Item to Mealie: Post Request Failed! JSON: " + str(req.json())
                )
            except:
                raise DropItem(
                    "Add Item to Mealie: Post Request and Retrieving JSON Error Failed! Status Code: " + str(req.status_code) + "\nText: " + req.text
                )

        # Continue to next pipeline
        return item


# Pipeline to Include Current Recipe in Cache DB
class AddItemToCache:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Open connection with cache DB
        conn = sqlite3.connect("/usr/src/app/mealie_scraper/cache.db")
        cursor = conn.cursor()

        # Insert the current recipe
        cursor.execute(
            "INSERT INTO cachedRecipes (slug) VALUES (?)", (adapter.get("slug"),)
        )

        conn.commit()

        # Close DB connection
        cursor.close()
        conn.close()

        # This is the last item pipeline
        return item
