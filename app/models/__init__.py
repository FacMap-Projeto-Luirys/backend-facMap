"""Modelos (tabelas) do banco. Importar daqui garante que todos ficam registrados no Base."""

from app.models.assessment import Assessment
from app.models.user import User

__all__ = ["Assessment", "User"]
