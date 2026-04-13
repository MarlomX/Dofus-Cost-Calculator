from backend.object.item import Item
from backend.object.ingredient import Ingredient

class ItemService:

    def build_item(value : dict, ingredients: list[Ingredient] = None) -> Item:  
        """
        Monta um objeto Item a partir de um dicionário de valores e uma lista de Ingredient.

        Parâmetros:
            value       — dict com id, name, name_search, level, price, has_recipe
            ingredients — lista de objetos Ingredient já montados (pode ser None ou [])
        """

        item = Item(
            id = value.get("id"),
            name = value.get("name"),
            level = value.get("level", "?"),
            price = value.get("price", 0),
            has_recipe= value.get("has_recipe"),
            ingredients = ingredients if ingredients else [],
            type_name  = value.get("type_name", "Desconhecido"),
            super_type_name = value.get("super_type_name", "Desconhecido")
        )

        return item