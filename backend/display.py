from object.item import Item
from dofus_api import fetch_item_by_id

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

        if len(item.ingredients) > 0:

            print(f"  Buscando {len(item.ingredients)} ingrediente(s)...")

            total_cost = 0
            
            for ingredient in item.ingredients:
                item_ingredient = fetch_item_by_id(ingredient.item_id)

                print(f"    • {ingredient.quantity} x  {item_ingredient.name} Preço: {item_ingredient.price} kamas (estimado)".replace(",", "."))
                total_cost += item_ingredient.price * ingredient.quantity
            
            print(f"  Custo:  {total_cost:,} kamas (estimado)".replace(",", "."))

        else:
            print("    Receita não encontrada.")
    else:
        print("  Craft:  Não")

    print("=" * 40 + "\n")