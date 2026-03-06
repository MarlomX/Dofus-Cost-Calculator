from dofus_api import fetch_item_by_name_search
from display import display_item
import database

def main():
    database.init_database()
    search_name = input("Digite o nome do item: ").strip()
    item = fetch_item_by_name_search(search_name)

    if item:
        display_item(item)


if __name__ == "__main__":
    main()