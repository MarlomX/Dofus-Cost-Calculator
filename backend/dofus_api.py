import requests
import database
from item import Item
from item_repository import ItemRepository
import unicodedata


# URL base da API pública do DofusDB
BASE_URL = "https://api.dofusdb.fr"

def normalize_name(name: str) -> str:
    """Remove acentos e converte para minúsculo para uso na busca."""
    # NFD separa o caractere base do acento (ex: "á" vira "a" + acento combinado)
    # encode/decode ascii ignora os acentos combinados, deixando só o base
    normalized = unicodedata.normalize("NFD", name)
    return normalized.encode("ascii", "ignore").decode("ascii").lower().strip()

def clear_item(api_item, name_search):
    clean_item = {
    "id":          api_item["id"],
    "name":        api_item["name"]["pt"],
    "name_search": name_search,
    "level":       api_item["level"],
    "price":       api_item.get("price", 0),
    "has_recipe":  api_item.get("hasRecipe", False)
}
    
    if clean_item["has_recipe"]:
        recipe = fetch_recipe(clean_item["id"])

        ids = recipe["ingredientIds"]
        quantities = recipe["quantities"]

        clean_item["ingredients"] = [
            {"ingredient_id": ing_id, "quantity": qty}
            for ing_id, qty in zip(ids, quantities)
        ]
    else:
        clean_item["ingredients"] = []
    
    return clean_item


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
    
    clean_item = clear_item(api_item, name_search)
    
    item = ItemRepository.mont_item(clean_item)

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
    
    item = ItemRepository.mont_item(clean_item)

    ItemRepository.save_in_db(item= item)

    return item

def fetch_recipe(item_id: int) -> dict | None:
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
        return None

    data = response.json()

    if not data.get("data"):
        return None

    return data["data"][0]


def fetch_ingredient_values(ingredient_id: int) -> dict:
    """
    Busca o nome e o preço dos igredientes apartir do id do igrediente.
    Retorna um dicionario com os valores name e price
    """

    url = f"{BASE_URL}/items/{ingredient_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return {        
        "name": "",
        "price": 0
    }
    
    data = response.json()
    
    name = data.get("name", {}).get("pt", f"Ingrediente #{ingredient_id}")
    price = data.get("price")
 
    return {        
        "name": name,
        "price": price
    }


def fetch_ingredients(ingredient_ids: list, quantities: list) -> list[dict]:
    """
    Para cada ID de ingrediente, busca o nome e monta uma lista de dicionários
    com { name, quantity }.
    """
    ingredients = []

    for ingredient_id, quantity in zip(ingredient_ids, quantities):
        values = fetch_ingredient_values(ingredient_id)
        ingredients.append({
            "name": values["name"],
            "quantity": quantity,
            "price" : values["price"]
        })

    return ingredients


def display_item(item: Item) -> None:
    """
    Exibe as informações do item no terminal.
    Se for craftável, busca e exibe a lista de ingredientes com quantidades.
    """

    print("\n" + "=" * 40)
    print(f"  Item:   {item.name}")
    print(f"  Nível:  {item.level}")
    print(f"  Preço:  {item.price:,} kamas (estimado)".replace(",", "."))

    # Se tiver receita, busca e exibe os ingredientes
    if item.has_recipe and item.id:
        print("\n  Receita de Craft:")

        recipe = fetch_recipe(item.id)

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

    print("=" * 40 + "\n")


# Ponto de entrada — roda direto pelo terminal
if __name__ == "__main__":

    database.init_database()
    search_name = input("Digite o nome do item: ").strip()
    item = fetch_item_by_name_search(search_name)

    if item:
        display_item(item)