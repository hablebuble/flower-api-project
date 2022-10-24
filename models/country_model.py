from typing import Optional
from sqlmodel import SQLModel, Field


class CountryBase(SQLModel):
    name_english: str = Field(index=True)
    name_russian: str = Field(index=True)
    country_count: str = Field(index=True)


class Country(CountryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class CountryCreate(CountryBase):
    pass


class CountryRead(CountryBase):
    id: int