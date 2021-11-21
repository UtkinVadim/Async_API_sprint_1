from functools import lru_cache
from typing import Optional, List, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from models.person import Person
from models.genre import Genre

# FIXME: вынести это в настройки
# FIXME: добавить время кеша на жанры и персоналии
FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.models = {
            "movies": Film,
            "genre": Genre,
            "person": Person,
        }

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, id_: str, index: str) -> Optional[Film]:
        """
        Возвращает объект по id из указанного индекса. Сначала ищет объект в кеше,
        при отсутствии: берёт из базы, кладёт в кеш, возвращает найденный объект.

        :param id_:
        :param index:
        :return:
        """
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        obj = await self._get_from_cache_by_id(id_, index)
        if not obj:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            obj = await self._get_by_id_from_elastic(id_, index)
            if not obj:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_obj_to_cache(obj)
        return obj

    async def search(self, index: str, body: dict) -> List:
        doc = await self.elastic.search(index=index, body=body)
        doc = doc.get("hits", {})
        doc = doc.get("hits", [])
        doc = [Film(**d["_source"]) for d in doc]
        return doc

    async def _get_by_id_from_elastic(self, id_: str, index: str) -> Optional[Film]:
        doc = await self.elastic.get(index, id_)
        data_model = self.models[index]
        return data_model(**doc["_source"])

    async def _get_from_cache_by_id(self, id_: str, index: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(id_)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        data_model = self.models[index]
        obj = data_model.parse_raw(data)
        return obj

    async def _put_obj_to_cache(self, obj: Union[Film]):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(obj.id, obj.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
