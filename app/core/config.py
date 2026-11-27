from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas do arquivo .env (ou de variáveis de ambiente)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "file:./facmap.db"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173"
    # Opcional: libera também as URLs de preview da Vercel, ex.: https://frontend-fac-map-.*\.vercel\.app
    cors_origin_regex: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        """Origens liberadas no CORS.

        O navegador envia a origem exatamente como `https://dominio` (com esquema e sem barra no fim).
        Um valor como `frontend-fac-map.vercel.app` ou `https://frontend-fac-map.vercel.app/` nunca
        bateria e o front receberia erro de conexão, então completamos o esquema e tiramos a barra.
        """
        origins = []
        for raw in self.cors_origins.split(","):
            origin = raw.strip().strip('"').rstrip("/")
            if not origin:
                continue
            if "://" not in origin:
                origin = f"https://{origin}"
            origins.append(origin)
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
