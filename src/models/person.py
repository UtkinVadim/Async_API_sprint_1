from typing import List, Optional

from pydantic import BaseModel

from models.base_orjson_model import BaseOrjsonModel


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]
    role: str


class Person(BaseOrjsonModel):
    id: str
    fullname: str
    film_ids: Optional[List[Film]]
