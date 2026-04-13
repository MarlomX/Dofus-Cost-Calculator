from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configurações da aplicação lidas do arquivo .env.
    Pydantic-settings faz a leitura e validação automaticamente.
    """

    # Feature flags — controlam o comportamento por versão (pública vs pessoal)
    enable_price_edit: bool = False
    enable_ocr: bool = False

    # Servidor padrão do Dofus (usado na tabela item_prices no futuro)
    default_server: str = "Draconiros"

    # CORS — lista de origens permitidas separadas por vírgula no .env
    # Exemplo no .env: CORS_ORIGINS=https://meusite.vercel.app,http://localhost:3000
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instância global — importada em main.py e nos routers que precisam das flags
settings = Settings()