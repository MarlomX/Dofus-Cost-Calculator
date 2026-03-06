from unicodedata import normalize

def normalize_name(name: str) -> str:
    """Remove acentos e converte para minúsculo para uso na busca."""
    # NFD separa o caractere base do acento (ex: "á" vira "a" + acento combinado)
    # encode/decode ascii ignora os acentos combinados, deixando só o base
    normalized = normalize("NFD", name)
    return normalized.encode("ascii", "ignore").decode("ascii").lower().strip()

def clear_item(api_item):
    return {
    "id":          api_item["id"],
    "name":        api_item["name"]["pt"],
    "name_search": normalize_name(api_item["name"]["pt"]),
    "level":       api_item["level"],
    "price":       api_item.get("price", 0),
    "has_recipe":  api_item.get("hasRecipe", False)
}
    