from object.item import Item

def display_item(item: Item) -> None:
    """
    Exibe as informações do item no terminal.
    Se for craftável, busca e exibe a lista de ingredientes com quantidades.
    """

    print("\n" + "=" * 40)
    print(f"  Item:   {item.name}")
    print(f"  Nível:  {item.level}")
    print(f"  Categoria:   {item.type_name} - ({item.super_type_name})")
    print(f"  Preço:  {item.price:,} kamas (estimado)".replace(",", "."))

    # Se tiver receita, busca e exibe os ingredientes
    if item.has_recipe and item.ingredients:
        job_name = item.ingredients[0].job_name
        print(f"  Profissão:   {job_name}")
        print("\n  Receita de Craft:")
        total_cost = 0
        for ingredient in item.ingredients:
            print(f"    • {ingredient.quantity} x  {ingredient.name} Preço: {ingredient.price} kamas (estimado)".replace(",", "."))
            total_cost += ingredient.price * ingredient.quantity
        print(f"  Custo:  {total_cost:,} kamas (estimado)".replace(",", "."))

    elif item.has_recipe:
        print("    Receita não encontrada.")
    else:
        print("  Craft:  Não")

    print("=" * 40 + "\n")