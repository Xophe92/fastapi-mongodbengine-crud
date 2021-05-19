from typing import Optional, List

from fastapi import FastAPI, Body, Header, Cookie
from fastapi import status

from pydantic import BaseModel, Field


from mongoengine import connect
from mongoengine import Document, EmbeddedDocument
from mongoengine import StringField, FloatField, EmbeddedDocumentField


from bson.objectid import ObjectId


class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')

class Tax(BaseModel):
    name: str
    rate: float
    class Config:
        orm_mode = True

class TaxDB(EmbeddedDocument):
    name = StringField(required=True)
    rate = FloatField(required=True)


class Item(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[Tax] = None

    class Config:
        orm_mode = True
        json_encoders = {
            ObjectId: str
        }            


class ItemDB(Document):
    name = StringField(required=True)
    description = StringField(max_length=50)
    price = FloatField(required=True)
    tax = EmbeddedDocumentField(TaxDB)



app = FastAPI()
connect("fast-api-mongodb")
ItemDB.objects().delete()


@app.get("/items/", response_model=List[Item], tags=["utile"], status_code=status.HTTP_200_OK) 
def list_items():
    return ([Item.from_orm(obj).dict() for obj in ItemDB.objects])


@app.post("/items/", response_model=Item, tags=["utile"], status_code=status.HTTP_201_CREATED) 
async def create_item(item: Item = Body(
    ...,
    examples = {
        "normal" : {
            "summary" : "Base case",
            "description" : "The base case scenario with embedded object",
            "value": {
                "name" : "Christophe",
                "price" : 2048, 
                "tax" : {
                    "name" : "TVA",
                    "rate" : 19.6
                }
            }
        },

        "expensive" : {
            "summary" : "Expensive case",
            "description" : "An alternative scenario",
            "value": {
                "name" : "Christophe",
                "price" : 4096
            }
        }
    }
)) -> Item:
    """ Add a new item in the database.
    """
    new_db_item = ItemDB(**item.dict())
    new_db_item.save()
    
    return Item.from_orm(new_db_item)


@app.delete("/items/{id}", response_model=Item, tags=["utile"], status_code=status.HTTP_202_ACCEPTED) 
def delete_items(id: str):
    found_db_item = ItemDB.objects(id=id).first()
    item_deleted = Item.from_orm(found_db_item)
    found_db_item.delete()
    return item_deleted



@app.get("/user-agent/", tags=["inutile"])
async def read_user_agent(user_agent: Optional[str] = Header(None)):
    return {"User-Agent": user_agent}

@app.get("/cookie/", tags=["inutile"])
async def read_cookie(cookie_value: Optional[str] = Cookie(None)):
    return {"cookie_value": cookie_value}