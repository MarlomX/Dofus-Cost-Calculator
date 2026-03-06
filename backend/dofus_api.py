import requests
from utils import normalize_name, clear_item
from object.item import Item
from repository.item_repository import ItemRepository
from service.item_service import ItemService


# URL base da API pública do DofusDB
BASE_URL = "https://api.dofusdb.fr"

def fetch_item_by_name_search(name_search: str) -> Item | None:
    """
    Busca um item pelo nome em português na API do DofusDB.
    Retorna um dicionário com os dados do item, ou None se não encontrado.
    """

    name_search = normalize_name(name_search)

    result = ItemRepository.search_item_by_name_search(name_search= name_search)

    if result:
        return result

    url = f"{BASE_URL}/items"
    params = {
        "slug.pt": name_search,
        "$limit": 1
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code}")
        return None

    data = response.json()

    if not data.get("data"):
        print(f"Nenhum item encontrado para: '{name_search}'")
        return None
    
    api_item = data["data"][0]
    
    clean_item = clear_item(api_item)

    recipe = fetch_recipe(clear_item["id"])
    
    item = ItemService.mont_item(clean_item, recipe)

    ItemRepository.save_in_db(item= item)

    return item

def fetch_item_by_id(id: int) -> Item | None:
    """
    Busca um item pelo nome em português na API do DofusDB.
    Retorna um dicionário com os dados do item, ou None se não encontrado.
    """


    result = ItemRepository.search_item_by_id(id= id)

    if result:
        return result

    url = f"{BASE_URL}/items?={id}"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code}")
        return None

    data = response.json()

    if not data.get("data"):
        print(f"Nenhum item encontrado para: '{id}'")
        return None
    
    api_item = data["data"][0]
    
    clean_item = clear_item(api_item, normalize_name(api_item["name"]["pt"]))
    
    item = Item.mont_item(clean_item)

    ItemRepository.save_in_db(item= item)

    return item

def fetch_recipe(item_id: int) -> dict :
    """
    Busca a receita de craft de um item pelo seu ID.
    Retorna um dicionário com ingredientIds e quantities, ou None se não encontrado.
    """
    url = f"{BASE_URL}/recipes"
    params = {
        "resultId": item_id,
        "$select[]": ["ingredientIds", "quantities"]
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Erro ao buscar receita: {response.status_code}")
        return []

    data = response.json()

    if not data.get("data"):
        return []
    
    

    return data["data"][0]
