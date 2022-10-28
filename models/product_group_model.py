from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .country_model import Country


class ProductGroupBase(SQLModel):
    name: str = Field(index=True)
    code: str = Field(index=True, unique=True)

class ProductGroup(ProductGroupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductGroupCreate(ProductGroupBase):
    pass


class ProductGroupRead(ProductGroupBase):
    id: int


class ProductGroupUpdate(SQLModel):
    name: Optional[str] = None
    code: Optional[str] = None