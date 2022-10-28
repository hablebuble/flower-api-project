from typing import Optional, TYPE_CHECKING, List, ForwardRef
from sqlmodel import SQLModel, Field, Relationship


class CountryProductGroupLink(SQLModel, table=True):
    country_id: Optional[int] = Field(
        default=None, foreign_key="country.id", primary_key=True
    )
    productGroup_id: Optional[int] = Field(
        default=None, foreign_key="productgroup.id", primary_key=True)

class CountryGroupBuyerLink(SQLModel, table=True):
    country_id: Optional[int] = Field(
        default=None, foreign_key="country.id", primary_key=True
    )
    productGroup_id: Optional[int] = Field(
        default=None, foreign_key="productgroup.id", primary_key=True)

    buyer_id: Optional[int] = Field(
        default=None, foreign_key="buyer.id", primary_key=True)





class CountryBase(SQLModel):
    name_english: str = Field(index=True)
    name_russian: str = Field(index=True)
    country_code: str = Field(index=True)


class Country(CountryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)




class CountryCreate(CountryBase):
    pass


class CountryRead(CountryBase):
    id: int

class CountryReadWithGroup(CountryRead):
    product_groups: List['ProductGroupRead'] = []

class CountryUpdate(SQLModel):
    name_english: Optional[str] = None
    name_russian: Optional[str] = None
    country_code: Optional[str] = None




