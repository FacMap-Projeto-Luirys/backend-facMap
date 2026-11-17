from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, hash_password, verify_password
from app.database import db
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="E-mail ou senha incorretos.",
    headers={"WWW-Authenticate": "Bearer"},
)


def _token_response(user) -> TokenResponse:
    token, expires_in = create_access_token(user.id)
    return TokenResponse(access_token=token, expires_in=expires_in, user=UserResponse.model_validate(user))


async def _authenticate(email: str, password: str):
    user = await db.user.find_unique(where={"email": email.strip().lower()})
    if user is None or not user.isActive or not verify_password(password, user.hashedPassword):
        raise INVALID_CREDENTIALS
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):
    """Cria a conta e já devolve o token, para o usuário entrar direto."""
    if await db.user.find_unique(where={"email": data.email}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma conta com este e-mail.")

    user = await db.user.create(
        data={"name": data.name, "email": data.email, "hashedPassword": hash_password(data.password)}
    )
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """Login com JSON ({ email, password }) — usado pelo frontend."""
    return _token_response(await _authenticate(data.email, data.password))


@router.post("/token", response_model=TokenResponse, include_in_schema=True)
async def login_form(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login via formulário OAuth2 (campo `username` = e-mail). Usado pelo botão Authorize do /docs."""
    return _token_response(await _authenticate(form.username, form.password))
