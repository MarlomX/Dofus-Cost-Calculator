from fastapi import APIRouter, Depends, HTTPException

from backend.config import settings
from backend.repository.item_repository import ItemRepository
from backend.schemas.price_schema import PriceUpdate, PriceResponse

router = APIRouter(prefix="/items", tags=["prices"])


def require_price_edit():
    """
    Dependência que bloqueia a rota se ENABLE_PRICE_EDIT=false.
    Retorna 403 na versão pública — a rota existe, mas não opera.
    """
    if not settings.enable_price_edit:
        raise HTTPException(
            status_code=403,
            detail="Edição manual de preços desabilitada nesta instância.",
        )


@router.patch(
    "/{item_id}/price",
    response_model=PriceResponse,
    dependencies=[Depends(require_price_edit)],
)
def update_price(item_id: int, body: PriceUpdate):
    """
    Atualiza o preço de um item manualmente.
    Exclusivo da versão pessoal (ENABLE_PRICE_EDIT=true no .env).
    """
    repo = ItemRepository()
    item = repo.search_item_by_id(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    repo.update_price(item_id, body.price)

    return PriceResponse(item_id=item_id, price=body.price)