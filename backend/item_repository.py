import database
from item import Item
from ingredient import Ingredient

class ItemRepository:

    def save_in_db(item = Item):
        database.save_item(item_id= item.id,
                           name= item.name,
                           name_search= item.name_search,
                           level= item.level,
                           price= item.price,
                           has_recipe= item.has_recipe)
    
    def search_item_by_name_search(name_search = str) -> Item | None:
        result = database.is_item_cachedd(name_search=name_search)

        if result:
            values = database.get_item_by_name_search(name_search= name_search)
            item = ItemRepository.mont_item(values)

            return item
            

        return None
    
    def search_item_by_id(id = int) -> Item | None:
        result = database.is_item_cached(item_id=id)

        if result:
            values = database.get_item_by_id(item_id= id)
            item = ItemRepository.mont_item(values)

            return item
            

        return None

    
    def mont_item(paraments = dict) -> Item:  

        ingredients = []
        print(f"paraments= {paraments}")


        for ingredient in paraments["ingredients"]:
            print(f"ingredient= {ingredient}")
            ingredients.append( Ingredient(item_id =ingredient["ingredient_id"], quantity = ingredient["quantity"]))
             

        return Item(id= paraments.get("id"),
                name = paraments.get("name"),
                name_search= paraments.get("name_search"),
                level = paraments.get("level", "?"),
                price = paraments.get("price", 0),
                ingredients = ingredients
                )
    
"""
    if recipe:
            ingredient_ids = recipe.get("ingredientIds", [])
            quantities = recipe.get("quantities", [])

            print(f"  Buscando {len(ingredient_ids)} ingrediente(s)...")
            ingredients = fetch_ingredients(ingredient_ids, quantities)
            cost = 0

            for ingredient in ingredients:
                print(f"    • {ingredient['quantity']}x  {ingredient['name']} Preço: {ingredient['price']} kamas (estimado)".replace(",", "."))
                cost += ingredient["price"] * ingredient["quantity"]
            
            print(f"  Custo:  {cost:,} kamas (estimado)".replace(",", "."))

        else:
            print("    Receita não encontrada.")
    else:
        print("  Craft:  Não")
    
"""
        