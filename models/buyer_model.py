from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import date


class BuyerBase(SQLModel):
    date_of_birth: date
    name: str = Field(index=True)
    surname: str = Field(index=True)
    email: str = Field(index=True)
    phone: str = Field(index=True)
    telegram: str = Field(index=True, unique=True)
    is_working: bool


class Buyer(BuyerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class BuyerCreate(BuyerBase):
    is_working: Optional[bool] = False


class BuyerRead(BuyerBase):
    id: int


class BuyerUpdate(SQLModel):
    date_of_birth: Optional[date] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram: Optional[str] = None
    is_working: Optional[bool] = None
