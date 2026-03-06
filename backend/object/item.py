from object.ingredient import Ingredient
from dataclasses import dataclass

@dataclass
class Item:

    id : int
    name : str
    name_search : str
    level : int
    price : int
    has_recipe : bool
    ingredients : list[Ingredient]

    def add_ingredient(self, igredient):
        self.ingredients.append(igredient)




    


