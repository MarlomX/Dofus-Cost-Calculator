import database
from object.ingredient import Ingredient

class IngredientRepository:
      
    def get_ingredients_by_item_id(item_id = int) -> list[Ingredient]:
        """
        Busca os ingredientes de um item no banco pelo item_id.
        Retorna uma lista de objetos Ingredient.
        """
         
        ingredients = []
        ingredients_values = database.get_igredient_by_item_id(item_id)

        if not ingredients_values:
            return ingredients

        for value in ingredients_values:
            ingredient = Ingredient(
                ingredient_id = value["ingredient_id"], 
                quantity=value["quantities"]
                )
            ingredients.append(ingredient)

        return ingredients
    
    def save_ingredients(item_id: int, ingredients: list[dict]):
            """
            Salva os ingredientes de uma receita no banco.
            IMPORTANTE: cada ingrediente já deve estar salvo em 'items' antes desta chamada.

            Formato esperado:
                ingredients = [
                    {"ingredient_id": 123, "quantities": 5},
                    {"ingredient_id": 456, "quantities": 2},
                ]
            """
            database.save_ingredients(item_id=item_id, ingredients=ingredients)
            print(f"[IngredientRepository] {len(ingredients)} ingrediente(s) salvos para item_id={item_id}")
    
