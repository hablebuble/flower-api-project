from typing import List
import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends, Query, UploadFile, File
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select

from models.buyer_model import BuyerRead, Buyer, BuyerCreate, BuyerUpdate
from models.country_model import CountryRead, Country, CountryUpdate, CountryProductGroupLink, CountryGroupBuyerLink
from models.product_group_model import ProductGroupCreate, ProductGroup, ProductGroupRead
import pandas as pd

from utilities import insert_product_groups_from_file, insert_countries_from_file

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

def find_buyer():
    with Session(engine) as session:
        buyers = session.exec(select(Buyer.surname)).all()
        return list(buyers)

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
def create_link(group: str = Query(find_group()[1], enum=find_group()),
                country: str = Query(find_country()[1], enum=find_country()),
                session: Session = Depends(get_session)):
    q_country = select(Country.id).where(Country.name_russian == country)
    db_country = session.exec(q_country).first()
    q_group = select(ProductGroup.id).where(ProductGroup.name == group)
    db_group = session.exec(q_group).first()
    db_link = CountryProductGroupLink(country_id=db_country, productGroup_id=db_group)
    try:
        session.add(db_link)
        session.commit()
        session.refresh(db_link)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такое сопоставление уже существует в базе")
    return db_link



@app.get('/who-buying')
def who_buying(group:str, session: Session = Depends(get_session)):
    q_group = select(ProductGroup.id).where(ProductGroup.name.lower() == group.lower())


@app.post('/country-product-buyer-link')
def create_link(group: str = Query(find_group()[0], enum=find_group()),
                country: str = Query(find_country()[0], enum=find_country()),
                buyer: str = Query(find_buyer()[0], enum=find_buyer()),
                session: Session = Depends(get_session)):
    q_country = select(Country.id).where(Country.name_russian == country)
    db_country = session.exec(q_country).first()
    q_group = select(ProductGroup.id).where(ProductGroup.name == group)
    db_group = session.exec(q_group).first()
    q_buyer = select(Buyer.id).where(Buyer.surname == buyer)
    db_buyer = session.exec(q_buyer).first()
    db_link = CountryGroupBuyerLink(country_id=db_country, productGroup_id=db_group, buyer_id=db_buyer)
    try:
        session.add(db_link)
        session.commit()
        session.refresh(db_link)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такое сопоставление уже существует в базе")
    return db_link


@app.post('/upload-product-groups-csv')
def upload_csv(csvfile: UploadFile = File(...), session: Session = Depends(get_session)):
    df = pd.read_csv(csvfile.file, delimiter=";")
    dataframe = df.to_dict(orient='records')
    try:
        insert_product_groups_from_file(db=session, df=dataframe)
        return {'message': 'Success'}
    except:
        return {'message': 'Something went wrong'}


@app.post('/upload-coutnries-csv')
def upload_csv(csvfile: UploadFile = File(...), session: Session = Depends(get_session)):
    df = pd.read_csv(csvfile.file, delimiter=";")
    dataframe = df.to_dict(orient='records')
    try:
        insert_countries_from_file(db=session, df=dataframe)
        return {'message': 'Success'}
    except:
        return {'message': 'Something went wrong'}


## COUNTRY
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
    q_groups = select(CountryGroupBuyerLink.productGroup_id).where(CountryGroupBuyerLink.country_id == country_id)
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


@app.delete('/countries/{country_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_country(*, session: Session = Depends(get_session), country_id: int):
    db_country = session.get(Country, country_id)
    if not db_country:
        raise HTTPException(status_code=404, detail='Country not found')

    session.delete(db_country)
    session.commit()
    return


##PRODUCT GROUPS
@app.post('/product-groups/', response_model=ProductGroupRead)
def create_product_group(*, session: Session = Depends(get_session), product_group: ProductGroupCreate):
    db_product_group = ProductGroup.from_orm(product_group)
    session.add(db_product_group)
    session.commit()
    session.refresh(db_product_group)
    return db_product_group


@app.get('/product-groups/', response_model=List[ProductGroupRead])
def read_countries(*, session: Session = Depends(get_session)):
    product_groups = session.exec(select(ProductGroup)).all()
    return product_groups

@app.get('/product-groups/{product_group_id}')
def read_country(*, session: Session = Depends(get_session), product_group_id: int):
    db_product_group = session.get(ProductGroup, product_group_id).dict()
    q_countries = select(CountryGroupBuyerLink.country_id).where(CountryGroupBuyerLink.productGroup_id == product_group_id)
    db_countries = session.exec(q_countries).all()
    db_countries_list = []
    for i in set(db_countries):
        db_country = session.get(Country, i)
        db_countries_list.append(db_country)
    db_product_group["countries"] = db_countries_list
    if not db_product_group:
        raise HTTPException(status_code=404, detail='Country not found')
    return db_product_group


##BUYER
@app.get('/buyers', response_model=List[BuyerRead])
def read_buyers(*, session: Session = Depends(get_session)):
    buyers = session.exec(select(Buyer)).all()
    return buyers


@app.post('/buyers', response_model=BuyerRead)
def create_buyer(*, session: Session = Depends(get_session), buyer: BuyerCreate):
    db_buyer = Buyer.from_orm(buyer)
    session.add(db_buyer)
    session.commit()
    session.refresh(db_buyer)
    return db_buyer


@app.get('/buyers/{buyer_id}', response_model=BuyerRead)
def read_buyer(*, session: Session = Depends(get_session), buyer_id: int):
    db_buyer = session.get(Buyer, buyer_id)
    return db_buyer


@app.patch('/buyers/{buyer_id}', response_model=BuyerRead)
def update_buyer(*, session: Session = Depends(get_session), buyer_id: int, buyer: BuyerUpdate):
    db_buyer = session.get(Buyer, buyer_id)
    # print(db_buyer)
    if not db_buyer:
        raise HTTPException(status_code=404, detail='Buyer not found')
    buyer_data = buyer.dict(exclude_unset=True)
    for key, value in buyer_data.items():
        setattr(db_buyer, key, value)
    session.add(db_buyer)
    session .commit()
    session.refresh(db_buyer)
    return db_buyer



@app.delete('/buyers/{buyer_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_buyer(*, session: Session = Depends(get_session), buyer_id: int):
    db_buyer = session.get(Country, buyer_id)
    if not db_buyer:
        raise HTTPException(status_code=404, detail='Country not found')

    session.delete(db_buyer)
    session.commit()
    return



def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
    # uvicorn.run("main:app", host = "srvapi.macheliuk.ru", port=5000, log_level="info")
    uvicorn.run("main:app", host="localhost", port=5100, log_level="info", reload=True)
