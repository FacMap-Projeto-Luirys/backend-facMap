from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from prisma.models import User

from app.core.security import decode_access_token
from app.database import db

# tokenUrl aponta para a rota de formulário usada pelo botão "Authorize" do Swagger (/docs).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """Dependência para rotas protegidas: exige um JWT válido no header Authorization."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise unauthorized
    user = await db.user.find_unique(where={"id": user_id})
    if user is None or not user.isActive:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
