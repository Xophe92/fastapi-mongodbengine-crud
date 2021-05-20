
from typing import Optional, List



from fastapi import FastAPI, Body
from fastapi import status

from pydantic import BaseModel, Field

from elasticsearch import Elasticsearch



EXAMPLES = {
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


class Tax(BaseModel):
    name: str
    rate: float

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[Tax] = None

class ItemDB(BaseModel):
    id: str
    data: Item

app = FastAPI()
es = Elasticsearch()
es.indices.create(index="trades", ignore=400)


@app.get("/items/", response_model=List[ItemDB], tags=["utile"], status_code=status.HTTP_200_OK) 
def list_items():
    res = es.search(index="trades", body={}, size=10000)
    return [{"id" : hit["_id"], "data":hit["_source"] } for hit in res["hits"]["hits"]]


@app.post("/items/",
        response_model=ItemDB, 
        tags=["utile"], 
        status_code=status.HTTP_201_CREATED
        ) 
async def create_item(item: Item = Body(
    ...,
    examples = EXAMPLES
)) -> Item:
    """ Add a new item in the database.
    """
    res = es.index(index="trades", doc_type='trade', body=item.dict())
    newly_created_id = res["_id"]

    res = es.get(index="trades",id=newly_created_id)
    return {"id" : newly_created_id, "data":res["_source"] }


@app.delete("/items/{id}", 
        response_model=ItemDB, 
        tags=["utile"], 
        status_code=status.HTTP_202_ACCEPTED
        ) 
def delete_items(id: str):
    res = es.get(index="trades", id=id)
    es.delete(index="trades", id=id)
    return {"id":f"{id} - deleted", "data" : res["_source"] }


@app.put("/items/{id}", 
        response_model=ItemDB, 
        tags=["utile"], 
        status_code=status.HTTP_202_ACCEPTED
        ) 
async def update_item(id : str, item: Item = Body(
    ...,
    examples = EXAMPLES
)) -> Item:
    """ Add a new item in the database.
    """
    body = {"doc" : item.dict()}
    es.update(index="trades",id=id,body=body)

    res = es.get(index="trades", id=id)
    return {"id":id, "data":res["_source"] }
