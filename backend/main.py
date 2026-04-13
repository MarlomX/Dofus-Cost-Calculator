from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import items, prices
from backend.config import settings

# Cria a aplicação FastAPI com metadados para documentação automática (/docs)
app = FastAPI(
    title="Dofus Craft Calculator",
    description="API para calcular lucro de craft no Dofus.",
    version="0.1.0",
)

# Configura CORS — permite que o frontend (Vercel/Netlify) acesse o backend
# Em produção, substituir "*" pelo domínio real do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os routers com prefixo versionado
app.include_router(items.router, prefix="/api/v1")
app.include_router(prices.router, prefix="/api/v1")


@app.get("/health", tags=["status"])
def health_check():
    """Endpoint simples para verificar se o servidor está no ar."""
    return {"status": "ok"}