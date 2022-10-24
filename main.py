from typing import List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends, Query
from sqlalchemy import inspect
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models.country_model import CountryCreate, CountryRead, Country, CountryUpdate, ProductGroupCreate, ProductGroup, ProductGroupRead, ProductGroupUpdate, CountryProductGroupLink


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def find_country():
    with Session(engine) as session:
        countries = session.exec(select(Country.name_russian)).all()
        return list(countries)


def find_group():
    with Session(engine) as session:
        groups = session.exec(select(ProductGroup.name)).all()
        return list(groups)

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post('/country-product-link')
def create_link(group: str = Query('Яблоки', enum=find_group()), country: str = Query('Голландия', enum=find_country()), session: Session = Depends(get_session)):
    q_country = select(Country.id).where(Country.name_russian == country)
    db_country = session.exec(q_country).first()
    q_group = select(ProductGroup.id).where(ProductGroup.name == group)
    db_group = session.exec(q_group).first()
    db_link = CountryProductGroupLink(country_id=db_country, productGroup_id = db_group)
    session.add(db_link)
    session.commit()
    session.refresh(db_link)

    return db_link


@app.post('/countries/', response_model=CountryRead)
def create_country(name_russian, name_english, country_code, session: Session = Depends(get_session)):
    db_country = Country(name_russian=name_russian, name_english=name_english, country_code=country_code)
    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country


@app.get('/countries/', response_model=List[CountryRead])
def read_countries(*, session: Session = Depends(get_session)):

    countries = session.exec(select(Country)).all()
    return countries


@app.get('/countries/{country_id}')
def read_country(*, session: Session = Depends(get_session), country_id: int):

    db_country = session.get(Country, country_id).dict()
    q_groups = select(CountryProductGroupLink.productGroup_id).where(CountryProductGroupLink.country_id==country_id)
    db_groups = session.exec(q_groups).all()
    db_group_list = []
    for i in set(db_groups):
        db_group = session.get(ProductGroup, i)
        db_group_list.append(db_group)
    db_country["product_groups"] = db_group_list
    if not db_country:
        raise HTTPException(status_code=404, detail='Country not found')
    return db_country


@app.patch('/countries/{country_id}', response_model=CountryRead)
def update_country(*, session: Session = Depends(get_session), country_id: int, country: CountryUpdate):

    db_country = session.get(Country, country_id)
    if not db_country:
        raise HTTPException(status_code=404, detail='Country not found')
    country_data = country.dict(exclude_unset=True)
    for key, value in country_data.items():
        setattr(db_country, key, value)
    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country


@app.delete('/countries/{country_id}', status_code = status.HTTP_204_NO_CONTENT)
def delete_country(*, session: Session = Depends(get_session), country_id: int):

    db_country = session.get(Country, country_id)
    if not db_country:
        raise HTTPException(status_code=404, detail='Country not found')

    session.delete(db_country)
    session.commit()
    return


@app.post('/product-groups/', response_model=ProductGroupRead)
def create_country(*, session: Session = Depends(get_session), product_group: ProductGroupCreate):
    db_product_group = ProductGroup.from_orm(product_group)
    session.add(db_product_group)
    session.commit()
    session.refresh(db_product_group)
    return db_product_group


@app.get('/product-groups/', response_model=List[ProductGroupRead])
def read_countries(*, session: Session = Depends(get_session)):

    product_groups = session.exec(select(ProductGroup)).all()
    return product_groups


def main():
    create_db_and_tables()

if __name__ == "__main__":
    main()
    # uvicorn.run("main:app", host = "srvapi.macheliuk.ru", port=5000, log_level="info")
    uvicorn.run("main:app", host="localhost", port=5100, log_level="info", reload=True)
