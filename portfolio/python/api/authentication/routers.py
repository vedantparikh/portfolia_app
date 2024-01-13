from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .services import (
    authenticate_user,
    create_token,
    create_user,
    create_database,
    get_current_user,
    get_user_by_email,
    get_db,
)
from .schemas import UserCreate, User as UserSchema


create_database()
router = APIRouter(prefix='/auth', tags=['authentication'])


@router.post('/users')
async def user_creation(user: UserCreate, db: Session = Depends(get_db)):
    db_user = await get_user_by_email(email=user.email, db=db)
    if db_user:
        raise HTTPException(status_code=400, detail='Email already exists.')
    return await create_user(user=user, db=db)


@router.post('/token')
async def generate_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = await authenticate_user(
        email=form_data.username, password=form_data.password, db=db
    )
    if not user:
        raise HTTPException(status_code=401, detail='Invalid Credentials')

    return await create_token(user)

@router.get('/users/me', response_model=UserSchema)
async def get_user(token: str, db: Session = Depends(get_db)):
    return await get_current_user(token=token, db=db)