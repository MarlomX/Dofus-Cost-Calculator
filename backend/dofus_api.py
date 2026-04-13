import requests
from backend.utils import normalize_name, clear_item
from backend.object.item import Item
from backend.repository.item_repository import ItemRepository
from backend.repository.ingredient_repository import IngredientRepository


# URL base da API pública do DofusDB
BASE_URL = "https://api.dofusdb.fr"

def save_item_with_recipe(clean_item: dict, recipe: list[dict]) -> None:
    """
    Salva no banco o item principal e seus ingredientes.
    Cada ingrediente carrega o job_name vindo da receita.
    """

    ingredients_to_save = []
    for ing in recipe:
        ingredient_id = ing["ingredient_id"]
        quantity = ing["quantity"]
        job_name = ing["job_name"]

        if not ItemRepository.search_item_by_id(id=ingredient_id):
            fetch_item_by_id(ingredient_id)
        ingredients_to_save.append({
            "ingredient_id": ingredient_id,
            "quantity": quantity,
            "job_name": job_name,
        })

    ItemRepository.save_in_db_from_dict(clean_item)

    if ingredients_to_save:
        IngredientRepository.save_ingredients(
            item_id=clean_item["id"],
            ingredients=ingredients_to_save
        )

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
    recipe = fetch_recipe(item_id=clean_item["id"]) if clean_item["has_recipe"] else []
    
    save_item_with_recipe(clean_item=clean_item, recipe=recipe)
    
    # Monta e retorna o objeto Item com os ingredientes já preenchidos
    return ItemRepository.search_item_by_id(id = clean_item["id"])

def fetch_item_by_id(item_id: int, force_refresh: bool = False) -> Item | None:
    """
    Busca um item pelo ID na API do DofusDB.
    Primeiro verifica o cache local. Se não encontrar, busca na API e salva.
    Usado principalmente para buscar ingredientes de uma receita.
    Se force_refresh=False, tenta o cache primeiro.
    Se force_refresh=True, ignora o cache e re-busca na API (botão 'Atualizar').
    """

# Só usa o cache se não for um refresh forçado
    if not force_refresh:
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

    # Busca a receita caso este ingrediente também seja craftável
    recipe = fetch_recipe(item_id=clean_item["id"]) if clean_item["has_recipe"] else []

    save_item_with_recipe(clean_item=clean_item, recipe=recipe)

    # Monta e retorna o objeto Item sem ingredientes (ingrediente não tem receita aqui)
    return ItemRepository.search_item_by_id(id=clean_item["id"])

def fetch_job(job_id: int) -> str:
    """
    Busca o nome da profissão pelo ID.
    Retorna o nome em português ou 'Desconhecido' em caso de erro.
    """
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
 
    if response.status_code != 200:
        print(f"Erro ao buscar profissão job_id={job_id}: {response.status_code}")
        return "Desconhecido"
 
    data = response.json()
    return data.get("name", {}).get("pt", "Desconhecido")

def fetch_recipe(item_id: int) -> list[dict]:
    """
    Busca a receita de craft de um item pelo ID do item (resultId).
    Usa a rota /recipes?resultId={item_id} que retorna a receita cujo resultado é este item.
    """
    url_recipe = f"{BASE_URL}/recipes"
    response = requests.get(url_recipe, params={"resultId": item_id})

    if response.status_code != 200:
        print(f"Erro ao buscar receita para item_id={item_id}: {response.status_code}")
        return []

    data = response.json()

    # A rota retorna um wrapper com campo "data" contendo lista de receitas
    recipes = data.get("data", [])
    if not recipes:
        return []

    recipe = recipes[0]
    ingredient_ids = recipe.get("ingredientIds", [])
    quantities = recipe.get("quantities", [])
    job_name = fetch_job(recipe["jobId"]) if recipe.get("jobId") else "Desconhecido"


    return [
        {"ingredient_id": ing_id, "quantity": qty, "job_name": job_name}
        for ing_id, qty in zip(ingredient_ids, quantities)
    ]