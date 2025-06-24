import os
import sqlite3
import sys
import time

import requests

def initDB():
    if os.path.exists("/usr/src/app/mealie_scraper/cache.db"):
        os.remove("/usr/src/app/mealie_scraper/cache.db")

    # Create a cache database and get its cursor
    conn = sqlite3.connect("/usr/src/app/mealie_scraper/cache.db")
    cursor = conn.cursor()

    # Create the cached recipes table
    cursor.execute(
        "CREATE TABLE cachedRecipes (id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT)"
    )

    try:
        # Get a summary of all recipes
        req = requests.get(
            os.getenv("API_PATH", default="") + "/recipes/summary",
            params={"limit": 99999999},
            headers={"Authorization": "Bearer " + os.getenv("API_TOKEN")}
        )
    except requests.RequestException as err:
        print(f"populateDB: Mealie API not up yet! Retrying in 15 seconds...")
        time.sleep(15)
        initDB()
        return

    # Verify the request was successful
    if req.status_code == 200:
        recipes = []

        # Get only recipe slugs as a list
        for recipe in req.json():
            recipes.append((recipe["slug"],))

        # Insert all recipe slugs to the database
        cursor.executemany("INSERT INTO cachedRecipes (slug) VALUES (?)", recipes)

        conn.commit()

        # Close the database connection when done
        cursor.close()
        conn.close()
    # The request failed
    else:
        # Close the database connection when done
        cursor.close()
        conn.close()
        sys.exit("PopulateDB: Failed to get recipes summary!")

# Remove this if no longer using bash to start this script
initDB()
