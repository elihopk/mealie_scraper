import scrapy


class MealieScraperItem(scrapy.Item):
    name = scrapy.Field()
    slug = scrapy.Field()
    image = scrapy.Field()
    description = scrapy.Field()
    recipeCategory = scrapy.Field()
    aggregateRating = scrapy.Field()
    dateAdded = scrapy.Field()
    dateUpdated = scrapy.Field()
    recipeYield = scrapy.Field()
    recipeIngredient = scrapy.Field()
    recipeInstructions = scrapy.Field()
    totalTime = scrapy.Field()
    prepTime = scrapy.Field()
    cookTime = scrapy.Field()
    orgURL = scrapy.Field()
    keywords = scrapy.Field()