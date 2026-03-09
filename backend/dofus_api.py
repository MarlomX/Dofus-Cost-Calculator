import requests
from utils import normalize_name, clear_item
from object.item import Item
from repository.item_repository import ItemRepository
from repository.ingredient_repository import IngredientRepository


# URL base da API pública do DofusDB
BASE_URL = "https://api.dofusdb.fr"


def fetch_item_by_name_search(name_search: str) -> Item | None:
    """
    Busca um item pelo nome em português na API do DofusDB.
    Primeiro verifica o cache local (SQLite). Se não encontrar, busca na API,
    salva o item e seus ingredientes no banco, e retorna o objeto Item montado.
    """

    name_search = normalize_name(name_search)

    # Tenta retornar do cache primeiro
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

    #Busca a receita na API (Caso não tenha receita entrega uma lista vazia)
    recipe = fetch_recipe(clean_item["id"]) if clean_item["has_recipe"] else []
    
    #Garante que cada ingrediente exista no banco antes de salvar a receita
    ingredients_to_save = []
    for ing in recipe:
        ingredient_id = ing["ingredient_id"]
        quantity = ing["quantity"]

        # Busca o item-ingrediente na API caso ainda não esteja no cache
        if not ItemRepository.search_item_by_id(id=ingredient_id):
            fetch_item_by_id(ingredient_id)

        ingredients_to_save.append({
            "ingredient_id": ingredient_id,
            "quantities": quantity
        })
    
    #Salva o item principal no banco
    ItemRepository.save_in_db_from_dict(clean_item)

    #Salva os ingredientes da receita no banco
    if ingredients_to_save:
        IngredientRepository.save_ingredients(
            item_id=clean_item["id"],
            ingredients=ingredients_to_save
        )

    # Monta e retorna o objeto Item com os ingredientes já preenchidos
    return ItemRepository.search_item_by_id(id = clean_item["id"])


def fetch_item_by_id(item_id: int) -> Item | None:
    """
    Busca um item pelo ID na API do DofusDB.
    Primeiro verifica o cache local. Se não encontrar, busca na API e salva.
    Usado principalmente para buscar ingredientes de uma receita.
    """

    # Tenta retornar do cache primeiro
    result = ItemRepository.search_item_by_id(id= item_id)
    if result:
        return result

    url = f"{BASE_URL}/items/{item_id}"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code}")
        return None

    data = response.json()

    # A rota /items/{id} retorna o objeto diretamente (sem wrapper "data")
    api_item = data if "id" in data else data.get("data", [None])[0]

    if not api_item:
        print(f"Nenhum item encontrado para id: '{item_id}'")
        return None
    
    clean_item = clear_item(api_item)

    # Salva o ingrediente no banco (sem buscar receita — ingredientes simples não precisam)
    ItemRepository.save_in_db_from_dict(clean_item)

    # Monta e retorna o objeto Item sem ingredientes (ingrediente não tem receita aqui)
    return ItemRepository.search_item_by_id(id=clean_item["id"])

def fetch_recipe(item_id: int) -> list[dict] :
    """
    Busca a receita de craft de um item pelo seu ID.
    Retorna lista de dicts com 'ingredient_id' e 'quantity', ou lista vazia.

    Formato retornado:
        [
            {"ingredient_id": 123, "quantity": 5},
            {"ingredient_id": 456, "quantity": 2},
        ]
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
    
    recipe_data = data["data"][0]
    
    ingredient_ids = recipe_data.get("ingredientIds", [])
    quantities = recipe_data.get("quantities", [])

    # Combina as duas listas em uma lista de dicts legível
    return [
        {"ingredient_id": ing_id, "quantity": qty}
        for ing_id, qty in zip(ingredient_ids, quantities)
    ]