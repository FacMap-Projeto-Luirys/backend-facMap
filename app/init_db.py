"""
Cria no banco as tabelas que ainda não existem. Tabelas que já existem não são alteradas.

Uso (com o ambiente virtual ativado):  python -m app.init_db
"""

from app import models  # noqa: F401  (registra os modelos no Base)
from app.database import Base, engine


def main() -> None:
    Base.metadata.create_all(engine)
    print("Tabelas prontas:", ", ".join(Base.metadata.tables))


if __name__ == "__main__":
    main()
