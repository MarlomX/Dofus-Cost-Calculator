from backend.object.ingredient import Ingredient
from dataclasses import dataclass

@dataclass
class Item:

    id : int
    name : str
    level : int
    price : int
    has_recipe : bool
    ingredients : list[Ingredient]
    type_name       : str
    super_type_name : str
