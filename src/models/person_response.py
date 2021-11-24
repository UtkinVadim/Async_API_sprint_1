from typing import Dict, List, Optional

from models.base_orjson_model import BaseOrjsonModel


class PersonFilmResponse(BaseOrjsonModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]


class PersonResponse(BaseOrjsonModel):
    uuid: str
    full_name: str
    films: List[Dict]
