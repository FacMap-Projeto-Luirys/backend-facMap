from fastapi import APIRouter

from app.core.deps import CurrentUser
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser):
    """Rota protegida: devolve o usuário dono do token."""
    return user
