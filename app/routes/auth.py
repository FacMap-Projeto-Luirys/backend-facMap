from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.database import DbSession
from app.models import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="E-mail ou senha incorretos.",
    headers={"WWW-Authenticate": "Bearer"},
)

EMAIL_TAKEN = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma conta com este e-mail.")


def _token_response(user: User) -> TokenResponse:
    token, expires_in = create_access_token(user.id)
    return TokenResponse(access_token=token, expires_in=expires_in, user=UserResponse.model_validate(user))


def _authenticate(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not user.is_active or not verify_password(password, user.hashed_password):
        raise INVALID_CREDENTIALS
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession):
    """Cria a conta e já devolve o token, para o usuário entrar direto."""
    if db.scalar(select(User.id).where(User.email == data.email)) is not None:
        raise EMAIL_TAKEN

    user = User(name=data.name, email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # dois cadastros com o mesmo e-mail ao mesmo tempo
        db.rollback()
        raise EMAIL_TAKEN
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: DbSession):
    """Login com JSON ({ email, password }) — usado pelo frontend."""
    return _token_response(_authenticate(db, data.email, data.password))


@router.post("/token", response_model=TokenResponse, include_in_schema=True)
def login_form(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    """Login via formulário OAuth2 (campo `username` = e-mail). Usado pelo botão Authorize do /docs."""
    return _token_response(_authenticate(db, form.username, form.password))
