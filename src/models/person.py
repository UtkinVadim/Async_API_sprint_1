from typing import List, Optional

from pydantic import BaseModel

from models.base_data_model import BaseDataModel


class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]
    role: str


class Person(BaseDataModel):
    fullname: str
    film_ids: Optional[List[Film]]
