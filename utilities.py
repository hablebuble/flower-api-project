from models.product_group_model import ProductGroup
from models.buyer_model import Buyer
import pandas as pd
from sqlmodel import Session, SQLModel, create_engine, select
from models.country_model import Country, CountryGroupBuyerLink

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)
session = Session(engine)

def insert_product_groups_from_file(db, df):
    for i in df:
        print(i)
        db_product_group = ProductGroup(name=i['name'], code=i['code'])
        db.add(db_product_group)
        db.commit()

#
# df = pd.read_csv("group_country_buyer.csv", delimiter=";")
# dataframe = df.to_dict(orient='records')
# for i in dataframe:
#     q_country = select(Country.id).where(Country.name_russian == i['country_name'])
#
#     db_country = session.exec(q_country).first()
#     if db_country == None:
#         print(i['country_name'])
#     q_group = select(ProductGroup.id).where(ProductGroup.code == i['product_group_code'])
#     db_group = session.exec(q_group).first()
#     if db_group == None:
#         print(i['product_group_code'])
#     q_buyer = select(Buyer.id).where(Buyer.surname == i['buyer_surname'])
#     db_buyer = session.exec(q_buyer).first()
#     if db_buyer == None:
#         print(i['buyer_surname'])
#
#     # print(db_buyer, db_group, db_country)
#     # print(i['product_group_code'], i['country_name'], i['buyer_surname'])
#     q_link = select(CountryGroupBuyerLink).where(CountryGroupBuyerLink.country_id==db_country, CountryGroupBuyerLink.productGroup_id==db_group, CountryGroupBuyerLink.buyer_id==db_buyer)
#     db_link = session.exec(q_link).first()
#     if db_link == None:
#         db_link = CountryGroupBuyerLink(country_id=db_country, productGroup_id=db_group, buyer_id=db_buyer)
#         try:
#             session.add(db_link)
#             session.commit()
#         except Exception as e:
#             print(e)
#             continue
#     else:
#         continue


# Залить страны из файла
def insert_countries_from_file(db, df):
    for i in df:
        print(i)
        db_country = Country(name_russian=i['name_russian'], name_english=i['name_english'], country_code=i['country_code'])
        db.add(db_country)
        db.commit()

# def insert_group_country_buyer_from_file(db, df):

