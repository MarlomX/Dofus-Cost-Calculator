from ingredient import Ingredient
from dataclasses import dataclass

@dataclass
class Item:

    id : int
    name : str
    name_search : str
    level : int
    price : int
    ingredients : list[Ingredient]

    @property
    def has_recipe(self) -> bool:
        """Verdadeiro se o item possui ingredientes de craft."""
        return len(self.ingredients) > 0



    


