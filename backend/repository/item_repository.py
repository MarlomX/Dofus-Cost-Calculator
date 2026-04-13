from backend import database
from backend.object.item import Item
from backend.service.item_service import ItemService
from backend.repository.ingredient_repository import IngredientRepository
from backend.utils import normalize_name

class ItemRepository:

    def save_in_db_from_dict(values: dict):
        """Salva um item a partir de um dicionário limpo (vindo de clear_item)."""
        database.save_item(
            item_id=values["id"],
            name=values["name"],
            level=values["level"],
            price=values["price"],
            has_recipe=values["has_recipe"],
            type_name=values["type_name"],
            super_type_name=values["super_type_name"]
        )
    
    def search_item_by_name_search(name_search : str) -> Item | None:
        """
        Busca um item no cache pelo nome normalizado.
        Se encontrado, monta o objeto Item já com os ingredientes (se tiver receita)
        """

        normalized = normalize_name(name_search)
        values = database.get_item_by_name(normalized)
        
        if not values:
            return None
        
        #Busca os ingredientes no banco e passa para o serviço montar o Item
        ingredients = IngredientRepository.get_ingredients_by_item_id(values["id"])
        return ItemService.build_item(values, ingredients)
                
    def search_item_by_id(id : int) -> Item | None:
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
        return ItemService.build_item(values, ingredients)
            
        