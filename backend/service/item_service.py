from object.item import Item
from object.ingredient import Ingredient

class ItemService:

    def mont_item(value = dict, ingredients: list[Ingredient] = None) -> Item:  
        """
        Monta um objeto Item a partir de um dicionário de valores e uma lista de Ingredient.

        Parâmetros:
            value       — dict com id, name, name_search, level, price, has_recipe
            ingredients — lista de objetos Ingredient já montados (pode ser None ou [])
        """

        item = Item(
            id= value.get("id"),
            name = value.get("name"),
            name_search= value.get("name_search"),
            level = value.get("level", "?"),
            price = value.get("price", 0),
            has_recipe= value.get("has_recipe"),
            ingredients = ingredients if ingredients else []
        )

        return item