from fastapi import APIRouter, HTTPException, Query

from backend.dofus_api import fetch_item_by_name_search
from backend.repository.item_repository import ItemRepository
from backend.schemas.item_schema import ItemResponse, ItemListResponse

router = APIRouter(prefix="/items", tags=["items"])

# ─── Listagem ────────────────────────────────────────────────────────────────

@router.get("", response_model=ItemListResponse)
def list_items(
    name: str | None = Query(None, description="Busca por nome (normaliza acentos)"),
    super_type: str | None = Query(None, description="Ex: 'Recurso', 'Equipamento'"),
    type: str | None = Query(None, description="Ex: 'Troféu', 'Pena'"),
    job: str | None = Query(None, description="Profissão da receita, ex: 'Fabricante'"),
    min_level: int | None = Query(None, ge=1),
    max_level: int | None = Query(None, le=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """
    Retorna lista paginada de itens com receita.
    Quando 'name' é fornecido, tenta buscar na API do DofusDB se não estiver em cache.
    Os demais filtros operam apenas sobre o banco local.
    """
    if name:
        # fetch_item_by_name_search já faz cache no SQLite
        item = fetch_item_by_name_search(name)
        items = [item] if item else []
    else:
        repo = ItemRepository()
        items = repo.list_items(
            super_type=super_type,
            type=type,
            job=job,
            min_level=min_level,
            max_level=max_level,
            page=page,
            page_size=page_size,
        )

    return ItemListResponse(items=items, total=len(items), page=page, page_size=page_size)


# ─── Detalhe ─────────────────────────────────────────────────────────────────

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int):
    """
    Retorna um item completo com ingredientes.
    Usado pelo painel lateral de detalhe no frontend.
    """
    repo = ItemRepository()
    item = repo.search_item_by_id(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    return item


# ─── Refresh ─────────────────────────────────────────────────────────────────

@router.post("/{item_id}/refresh", response_model=ItemResponse)
def refresh_item(item_id: int):
    """
    Re-busca o item na API do DofusDB e atualiza o cache local.
    Acionado pelo botão 'Atualizar preços' no painel lateral.
    """
    from backend.dofus_api import fetch_item_by_id

    item = fetch_item_by_id(item_id, force_refresh=True)

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado na API do DofusDB.")

    return item