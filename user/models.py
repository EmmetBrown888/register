from datetime import date
from ormar import Model, Integer, String, Boolean, Date

from utils.meta import MainMeta


class User(Model):
    class Meta(MainMeta):
        pass

    id: int = Integer(primary_key=True)
    email: str = String(max_length=320, unique=True)
    phone: str = String(max_length=15, unique=True)
    birthday: date = Date()
    password_hash: str = String(max_length=200)
    is_confirm: bool = Boolean(default=False)
