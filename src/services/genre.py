from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from fastapi import Depends
from elasticsearch import AsyncElasticsearch

from db.redis import get_redis
from models.genre import Genre
from db.elastic import get_elastic
from core.config import CACHE_EXPIRE_IN_SECONDS


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = "genre"

    async def get_all_genres(self) -> Optional[List[Genre]]:
        genres = await self._get_all_genres_from_elastic()
        return genres

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic_by_id(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def _get_all_genres_from_elastic(self) -> Optional[List[Genre]]:
        docs = await self.elastic.search(index=self.index)
        return [Genre(**doc["_source"]) for doc in docs["hits"]["hits"]]

    async def _get_genre_from_elastic_by_id(self, genre_id: str) -> Optional[Genre]:
        doc = await self.elastic.get(self.index, genre_id)
        return Genre(**doc["_source"])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(genre.id, genre.json(), expire=CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
