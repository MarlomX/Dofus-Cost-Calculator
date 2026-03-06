import database
from object.ingredient import Ingredient

class IgredientRepository:
      
    def get_ingredients_by_item_id(item_id = int) -> list[Ingredient]:
        ingredients = []
        ingredients_values = database.get_igredient_by_item_id(item_id)

        print()
        for value in ingredients_values:
            ingredient = Ingredient(ingredient_id = value["ingredient_id"], quantity=value["quantity"])
            ingredients.append(ingredient)
        return ingredients
    
    #def save_recipe_in_db():
