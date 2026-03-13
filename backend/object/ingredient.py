from dataclasses import dataclass

@dataclass
class Ingredient:
    ingredient_id : int
    name : str
    price : int
    quantity: int
    job_name      : str
