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
    
    def list_items(
        super_type: str | None = None,
        type: str | None = None,
        job: str | None = None,
        min_level: int | None = None,
        max_level: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[Item]:
        """
        Retorna lista paginada de itens craftáveis com filtros opcionais.
        Monta o WHERE dinamicamente — só inclui a condição se o filtro foi passado.
        """
        conditions = ["has_recipe = 1"]  # base: só itens craftáveis
        params = []

        if super_type:
            conditions.append("super_type_name = ?")
            params.append(super_type)

        if type:
            conditions.append("type_name = ?")
            params.append(type)

        if min_level:
            conditions.append("level >= ?")
            params.append(min_level)

        if max_level:
            conditions.append("level <= ?")
            params.append(max_level)

        if job:
            # job fica em recipe_ingredients → subquery necessária
            conditions.append(
                "id IN (SELECT item_id FROM recipe_ingredients WHERE job_name = ?)"
            )
            params.append(job)

        where_clause = " AND ".join(conditions)
        offset = (page - 1) * page_size
        params.extend([page_size, offset])  # LIMIT e OFFSET vão por último

        rows = database.list_items_filtered(where_clause, params)

        items = []
        for row in rows:
            ingredients = IngredientRepository.get_ingredients_by_item_id(row["id"])
            items.append(ItemService.build_item(row, ingredients))

        return items

    def update_price(item_id: int, price: int) -> None:
        """Delega a atualização de preço para o database."""
        database.update_item_price(item_id=item_id, price=price)
            
        