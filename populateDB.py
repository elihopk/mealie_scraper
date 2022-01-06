import os
import sqlite3
import sys

import requests

def initDB():
    # Remove any existing database
    os.remove("mealie_scraper/cache.db")

    # Create a cache database and get its cursor
    conn = sqlite3.connect("mealie_scraper/cache.db")
    cursor = conn.cursor()

    # Create the cached recipes table
    cursor.execute(
        "CREATE TABLE cachedRecipes (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT)"
    )

    # Get a summary of all recipes
    req = requests.get(
        os.getenv("API_PATH", default="") + "/recipes/summary",
        params={"limit": 99999999},
        headers={"Authorization": "Bearer " + os.getenv("API_TOKEN")}
    )

    # Verify the request was successful
    if req.status_code == 200:
        recipes = []

        # Get only recipe slugs as a list
        for recipe in req.json():
            recipes.append(recipe["slug"])

        # Insert all recipe slugs to the database
        cursor.executemany("INSERT INTO cachedRecipes (slug) VALUES (?)", recipes)

        # Close the database connection when done
        conn.close()
    # The request failed
    else:
        # Close the database connection when done
        conn.close()
        sys.exit("PopulateDB: Failed to get recipes summary!")
