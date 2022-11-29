from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from enum import Enum

class Units(Enum):
    PCS = "шт."
    BUNCH = "пуч."
    BOX = "короб."


class ProductBase(SQLModel):
    vbn: str
    eng_desc: Optional[str] = Field(index=True)
    vbn_full: Optional[str] = Field(index=True)
    vbn_group: Optional[str] = None
    vbn_group_desc: Optional[str] = None
    vbn_group_rus_desc: Optional[str] = None
    subgroup_rus: Optional[str] = None
    sort_rus: Optional[str] = None
    color_rus: Optional[str] = None
    show_color: bool = True
    units: Units = None
    comment: Optional[str] = None
    show_comment: bool = False
    multiplicity: Optional[str] = None
    show_multiplicity: bool = False
    diameter: Optional[str] = None
    show_diameter: bool = False
    grower: Optional[str] = None
    show_grower: bool = False
    supplier: Optional[str] = None
    show_supplier: bool = False
    lenght: Optional[int] = 0
    show_lenght: bool = False


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int


class ProductUpdate(SQLModel):
    eng_desc: Optional[str] = Field(index=True)
    vbn_full: Optional[str] = Field(index=True)