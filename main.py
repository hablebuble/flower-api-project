from typing import List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, status
from h11._abnf import status_code
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models.country_model import CountryCreate, CountryRead, Country, CountryUpdate

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post('/countries/', response_model=CountryRead)
def create_country(country: CountryCreate):
    with Session(engine) as session:
        db_country = Country.from_orm(country)
        session.add(db_country)
        session.commit()
        session.refresh(db_country)
        return db_country


@app.get('/countries/', response_model=List[CountryRead])
def read_countries():
    with Session(engine) as session:
        countries = session.exec(select(Country)).all()
        return countries


@app.get('/countries/{country_id}', response_model=CountryRead)
def read_country(country_id: int):
    with Session(engine) as session:
        db_country = session.get(Country, country_id)
        if not db_country:
            raise HTTPException(status_code=404, detail='Country not found')
        return db_country


@app.patch('/countries/{country_id}', response_model=CountryRead)
def update_country(country_id: int, country: CountryUpdate):
    with Session(engine) as session:
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
def delete_country(country_id: int):
    with Session(engine) as session:
        db_country = session.get(Country, country_id)
        if not db_country:
            raise HTTPException(status_code=404, detail='Country not found')

        session.delete(db_country)
        session.commit()
        return

if __name__ == "__main__":
    # uvicorn.run("main:app", host = "srvapi.macheliuk.ru", port=5000, log_level="info")
    uvicorn.run("main:app", host="localhost", port=5100, log_level="info", reload=True)
