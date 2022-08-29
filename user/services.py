from fastapi import HTTPException, status

from .models import User
from .schemas import UserCreate, UserCode
from utils.crypt import crypt_pass


async def create_user(data: UserCreate) -> str:
    """
    Add to database user

    :param data: class 'user.schemas.UserCreate', parameters: email: str, phone: str, birthday: date, password: str
    :return: object
    """
    # Check exists User
    email_exist: bool = await User.objects.filter(email=data.email).exists()
    phone_exist: bool = await User.objects.filter(phone=data.phone).exists()
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    elif phone_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already exists"
        )

    # Crypt Password
    hash_pass: str = await crypt_pass(data.password)
    user: User = await User.objects.create(
        email=data.email,
        phone=data.phone,
        birthday=data.birthday,
        password_hash=hash_pass
    )
    return user.phone


async def get_user(data: UserCode):
    user: User = await User.objects.get(phone=data.phone)
    if user:
        await user.update(is_confirm=True)
        return {
            'id': user.id,
            'email': user.email,
            'phone': user.phone,
            'birthday': user.birthday,
            'is_confirm': user.is_confirm
        }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="An error occurred while retrieving data"
    )
