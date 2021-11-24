from models.base_orjson_model import BaseOrjsonModel


class GenreResponse(BaseOrjsonModel):
    uuid: str
    name: str
