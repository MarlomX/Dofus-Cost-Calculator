from object.item import Item
from repository.ingredient_repository import IgredientRepository
from service.ingredient_service import IngredientService

class ItemService:

    def mont_item(value = dict, recipe = dict) -> Item:  

            item = Item(id= value.get("id"),
                    name = value.get("name"),
                    name_search= value.get("name_search"),
                    level = value.get("level", "?"),
                    price = value.get("price", 0),
                    has_recipe= value.get("has_recipe"),
                    ingredients = []
                    )
            
            if item.has_recipe:

                print("test")
                for ingredient_values in recipe:
                    ingredient = IngredientService.mont_service(ingredient_values["ingredient_ids"], ingredient_values["quantities"])
                    print(ingredient)
                    item.add_ingredient(ingredient)

            return item