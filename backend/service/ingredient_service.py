from object.ingredient import Ingredient

class IngredientService:

    def mont_service(ingredient_id = int, quantity = int) -> Ingredient:
        return Ingredient(ingredient_id=ingredient_id, quantity=quantity)