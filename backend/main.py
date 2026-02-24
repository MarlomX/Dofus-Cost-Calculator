from dofus_api import fetch_item, display_item

def main():
    search_name = input("Digite o nome do item: ").strip()
    item = fetch_item(search_name)

    if item:
        display_item(item)


if __name__ == "__main__":
    main()
