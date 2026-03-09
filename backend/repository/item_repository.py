import database
from object.item import Item
from service.item_service import ItemService
from repository.ingredient_repository import IngredientRepository

class ItemRepository:

    def save_in_db(item: Item):
        """Salva um objeto Item no banco"""
        database.save_item(
            item_id= item.id,
            name= item.name,
            name_search= item.name_search,
            level= item.level,
            price= item.price,
            has_recipe= item.has_recipe
        )
    
    def save_in_db_from_dict(values: dict):
        """Salva um item a partir de um dicionário limpo (vindo de clear_item)."""
        database.save_item(
            item_id=values["id"],
            name=values["name"],
            name_search=values["name_search"],
            level=values["level"],
            price=values["price"],
            has_recipe=values["has_recipe"]
        )
    
    def search_item_by_name_search(name_search = str) -> Item | None:
        """
        Busca um item no cache pelo nome normalizado.
        Se encontrado, monta o objeto Item já com os ingredientes (se tiver receita)
        """

        if not database.is_item_cached_by_name_search(name_search=name_search):
            return None
        
        values = database.get_item_by_name_search(name_search=name_search)
        
        if not values:
            return None
        
        #Busca os ingredientes no banco e passa para o serviço montar o Item
        ingredients = IngredientRepository.get_ingredients_by_item_id(values["id"])
        return ItemService.mont_item(values, ingredients)
                
    def search_item_by_id(id = int) -> Item | None:
        """
        Busca um item no cache pelo ID.
        Se encontrado, monta o objeto Item já com os ingredientes (se tiver receita).
        """
        if not database.is_item_cached_by_item_id(item_id=id):
            return None
        
        values = database.get_item_by_id(item_id= id)

        if not values:
            return None

        # Busca os ingredientes no banco e passa para o serviço montar o Item
        ingredients = IngredientRepository.get_ingredients_by_item_id(values["id"])
        return ItemService.mont_item(values, ingredients)
            
        