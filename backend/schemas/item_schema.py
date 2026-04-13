from pydantic import BaseModel, field_serializer


class IngredientResponse(BaseModel):
    ingredient_id: int
    name: str
    price: int
    quantity: int
    job_name: str

    # Preço 0 significa desconhecido — o frontend deve tratar isso (ex: exibir "—")
    price_known: bool = True

    @field_serializer("price")
    def serialize_price(self, price: int) -> int:
        return price

    def model_post_init(self, __context):
        object.__setattr__(self, "price_known", self.price > 0)

    model_config = {"from_attributes": True}


class ItemResponse(BaseModel):
    id: int
    name: str
    level: int
    price: int
    has_recipe: bool
    type_name: str
    super_type_name: str
    ingredients: list[IngredientResponse] = []

    # Campos calculados — o backend calcula, o frontend apenas exibe
    craft_cost: int = 0
    profit: int = 0
    price_known: bool = True

    def model_post_init(self, __context):
        craft = sum(i.price * i.quantity for i in self.ingredients)
        object.__setattr__(self, "craft_cost", craft)
        object.__setattr__(self, "profit", self.price - craft)
        object.__setattr__(self, "price_known", self.price > 0)

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
    page: int
    page_size: int