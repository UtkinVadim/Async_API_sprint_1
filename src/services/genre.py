from functools import lru_cache

from aioredis import Redis
from fastapi import Depends
from elasticsearch import AsyncElasticsearch

from db.redis import get_redis
from models.genre import Genre
from db.elastic import get_elastic
from services.base_service import BaseService


class GenreService(BaseService):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)
        self.index = "genre"
        self.model = Genre


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
