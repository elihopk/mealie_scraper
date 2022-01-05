import os
import sqlite3
import sys

import requests

def initDB():
    os.remove("mealie_scraper/cache.db")
    conn = sqlite3.connect("mealie_scraper/cache.db")
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE cachedRecipes (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT)"
    )

    req = requests.get(
        os.getenv("API_PATH", default="") + "/recipes/summary",
        headers={"Authorization": "Bearer " + os.getenv("API_TOKEN")}
    )

    if req.status_code == 200:
        recipes = []

        for recipe in req.json():
            recipes.append(recipe["slug"])

        cursor.executemany("INSERT INTO cachedRecipes (slug) VALUES (?)", recipes)

        conn.close()
    else:
        conn.close()
        sys.exit("PopulateDB: Failed to get recipes summary!")
