# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MealieScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    name = scrapy.Field()
    slug = scrapy.Field()
    image = scrapy.Field()
    description = scrapy.Field()
    recipeCategory = scrapy.Field()
    rating = scrapy.Field()
    dateAdded = scrapy.Field()
    dateUpdated = scrapy.Field()
    recipeYield = scrapy.Field()
    recipeIngredient = scrapy.Field()
    recipeInstructions = scrapy.Field()
    totalTime = scrapy.Field()
    prepTime = scrapy.Field()
    performTime = scrapy.Field()
    orgURL = scrapy.Field()