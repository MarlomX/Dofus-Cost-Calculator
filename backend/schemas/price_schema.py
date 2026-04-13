from pydantic import BaseModel, Field


class PriceUpdate(BaseModel):
    price: int = Field(..., ge=0, description="Novo preço em kamas. 0 = desconhecido.")


class PriceResponse(BaseModel):
    item_id: int
    price: int