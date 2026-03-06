import database
from object.item import Item
from service.item_service import ItemService

class ItemRepository:

    def save_in_db(item = Item):
        database.save_item(item_id= item.id,
                           name= item.name,
                           name_search= item.name_search,
                           level= item.level,
                           price= item.price,
                           has_recipe= item.has_recipe)
    
    def search_item_by_name_search(name_search = str) -> Item | None:
        result = database.is_item_cached_by_name_search(name_search=name_search)

        if result:
            values = database.get_item_by_name_search(name_search= name_search)
            item = ItemService.mont_item(values)

            return item
            

        return None
    
    def search_item_by_id(id = int) -> Item | None:
        result = database.is_item_cached_by_item_id(item_id=id)

        if result:
            values = database.get_item_by_id(item_id= id)
            item = ItemService.mont_item(values)

            return item
            

        return None
            
        