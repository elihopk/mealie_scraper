import json
import os
import sys

import scrapy
from mealie_scraper.items import MealieScraperItem
from scrapy.linkextractors import LinkExtractor


class RecipesSpider(scrapy.Spider):
    name = "recipes"
    # Pass allowed_domains as environment variable ALLOWED_DOMAINS
    # TODO: Fix allowed_domains being required. Should be optional but breaks when empty
    # Looks to be caused by LinkExtractor getting allowed domains when it's still empty
    # Will probably need to move some code out of start_requests or maybe remove it alltogether
    allowed_domains = os.getenv("ALLOWED_DOMAINS", default="").split(" ")

    # Get urls from environment variable SEARCH_SITES separated by a space
    urls = os.getenv("SEARCH_SITES", default="").split(" ")

    # If the user did not provide any ALLOWED_DOMAINS, use the SEARCH_SITES
    if not allowed_domains:
        allowed_domains = []

        for domain in urls:
            allowed_domains.append(domain.split("/")[2])

    le = LinkExtractor(allow_domains=allowed_domains)

    def start_requests(self):
        # Exit if the user didn't provide any URLs
        if not self.urls:
            sys.exit("No Search Sites Provided!")

        # Make a Request for each URL
        for url in self.urls:
            self.logger.debug("Starting Request for URL " + url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.logger.debug("Parsing Response for " + response.url)

        # Variable to Track Decision on if Page is a Recipe
        isRecipe = True

        # All we'll need from any page for this is the JSON Linked Data and later links for all referenced pages
        recipeDataBytes = response.xpath(
            '//script[@type="application/ld+json"]//text()'
        ).get()
        recipeData = None

        # Verify that the page contained JSON-LD
        if recipeDataBytes:
            recipeData = json.loads(recipeDataBytes)
            if "@graph" in recipeData:
                recipeData = recipeData["@graph"]
        else:
            isRecipe = False

        # JSON-LD must have been loaded to run additional checks for a recipe
        if isRecipe:
            # Check if JSON-LD is provided as a list
            if isinstance(recipeData, list):
                # Loop for each JSON object until the one with recipe metadata is found
                for jsonObj in recipeData:
                    # Some sites provide @type as a list
                    if isinstance(jsonObj["@type"], list):
                        # Loop through each @type
                        for mdType in jsonObj["@type"]:
                            # Check if the current @type is a Recipe
                            if mdType == "Recipe":
                                recipeData = jsonObj
                                break
                            # If this is the last index and a Recipe @type wasn't found
                            elif mdType == jsonObj["@type"][-1]:
                                isRecipe = False
                    # @type was not a list
                    else:
                        # Check if the @type is Recipe
                        if jsonObj["@type"] == "Recipe":
                            recipeData = jsonObj
                            break
                    # If the last JSON object was not a recipe
                    if jsonObj == recipeData[-1]:
                        isRecipe = False
            # JSON-LD was not provided as a list
            else:
                # Check if @type was provided as a list
                if isinstance(recipeData["@type"], list):
                    # Loop through each @type
                    for mdType in recipeData["@type"]:
                        # If a recipe is found, nothing further needs done
                        if mdType == "Recipe":
                            break
                        # If this is the last index and the last check failed, this is not a recipe
                        elif mdType == recipeData["@type"][-1]:
                            isRecipe = False
                else:
                    # If there is one @type and one JSON object but no Recipe
                    if recipeData["@type"] != "Recipe":
                        isRecipe = False

        # Verify finally that the JSON-LD had a recipe
        if isRecipe:
            # Create an Item to start extracting JSON data into
            recipeItem = MealieScraperItem()

            # Extract Item properties from recipe JSON data
            recipeItem["name"] = recipeData["name"]

            # If there are multiple images only use the first one
            if isinstance(recipeData["image"], list):
                if isinstance(recipeData["image"][0], str):
                    recipeItem["image"] = recipeData["image"][0]
                else:
                    recipeItem["image"] = recipeData["image"][0]["url"]
            else:
                if isinstance(recipeData["image"][0], str):
                    recipeItem["image"] = recipeData["image"][0]
                else:
                    recipeItem["image"] = recipeData["image"]["url"]

            if "description" in recipeData:
                recipeItem["description"] = recipeData["description"]
            if "recipeCategory" in recipeData:
                recipeItem["recipeCategory"] = recipeData["recipeCategory"]
            if "aggregateRating" in recipeData:
                recipeItem["rating"] = round(
                    float(recipeData["aggregateRating"]["ratingValue"])
                )

            # Will need special formatting for datePublished and dateModified.
            # Some websites provide this in ISO8601 format
            # TODO: Handle datePublished and dateModified

            # if "datePublished" in recipeData:
            #     recipeItem["dateAdded"] = recipeData["datePublished"]
            # if "dateModified" in recipeData:
            #     recipeItem["dateUpdated"] = recipeData["dateModified"]

            if "recipeYield" in recipeData:
                if isinstance(recipeData["recipeYield"], list):
                    recipeItem["recipeYield"] = recipeData["recipeYield"][0]
                else:
                    recipeItem["recipeYield"] = recipeData["recipeYield"]
            if "recipeIngredient" in recipeData:
                recipeItem["recipeIngredient"] = []
                for ingredient in recipeData["recipeIngredient"]:
                    recipeItem["recipeIngredient"].append({"title": ingredient})
            if "recipeInstructions" in recipeData:
                if "itemListElement" in recipeData["recipeInstructions"][0]:
                    tempInstructions = []

                    for section in recipeData["recipeInstructions"]:
                        tempInstructions = tempInstructions + section["itemListElement"]

                    recipeItem["recipeInstructions"] = tempInstructions
                else:
                    recipeItem["recipeInstructions"] = recipeData["recipeInstructions"]
            if "totalTime" in recipeData:
                recipeItem["totalTime"] = recipeData["totalTime"]
            if "prepTime" in recipeData:
                recipeItem["prepTime"] = recipeData["prepTime"]
            if "cookTime" in recipeData:
                recipeItem["performTime"] = recipeData["cookTime"]

            recipeItem["orgURL"] = response.url

            yield recipeItem
        # Follow all links on page if the page is not a recipe
        else:
            self.logger.debug(
                'Recipe not found on "' + response.url + '"... Looking for links.'
            )

            for ln in self.le.extract_links(response):
                yield scrapy.Request(url=ln.url, callback=self.parse)
