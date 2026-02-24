import requests

# URL base da API pública do DofusDB
BASE_URL = "https://api.dofusdb.fr"


def fetch_item(name: str) -> dict | None:
    """
    Busca um item pelo nome em português na API do DofusDB.
    Retorna um dicionário com os dados do item, ou None se não encontrado.
    """
    url = f"{BASE_URL}/items"
    params = {
        "slug.pt": name.lower(),
        "$limit": 1
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code}")
        return None

    data = response.json()

    if not data.get("data"):
        print(f"Nenhum item encontrado para: '{name}'")
        return None

    return data["data"][0]


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


def display_item(item: dict) -> None:
    """
    Exibe as informações do item no terminal.
    Se for craftável, busca e exibe a lista de ingredientes com quantidades.
    """
    name = item.get("name", {}).get("pt", "Desconhecido")
    level = item.get("level", "?")
    price = item.get("price", 0)
    has_recipe = item.get("hasRecipe", False)
    item_id = item.get("id")

    print("\n" + "=" * 40)
    print(f"  Item:   {name}")
    print(f"  Nível:  {level}")
    print(f"  Preço:  {price:,} kamas (estimado)".replace(",", "."))

    # Se tiver receita, busca e exibe os ingredientes
    if has_recipe and item_id:
        print(f"\n  Receita de Craft:")

        recipe = fetch_recipe(item_id)

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
    search_name = input("Digite o nome do item: ").strip()
    item = fetch_item(search_name)

    if item:
        display_item(item)