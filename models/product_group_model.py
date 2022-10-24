from typing import Optional
from sqlmodel import SQLModel, Field


class ProductGroupBase(SQLModel):
    name: str = Field(index=True)
    code: str = Field(index=True, unique=True)


class ProductGroup(ProductGroupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductGroupCreate(ProductGroupBase):
    pass


class ProductGroupRead(ProductGroupBase):
    id: int
