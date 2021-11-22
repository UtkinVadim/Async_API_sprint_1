import hashlib
import json
import logging
from functools import lru_cache
from typing import Optional, Union

from aioredis import Redis
from core.config import CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from models.genre import Genre
from models.person import Person

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.models = {
            "movies": Film,
            "genre": Genre,
            "person": Person,
        }

    async def get_by_id(self, id_: str, index: str) -> Optional[Film, Person, Genre]:
        """
        Возвращает объект по id из указанного индекса. Сначала ищет объект в кеше,
        при отсутствии: берёт из базы, кладёт в кеш, возвращает найденный объект.

        :param id_:
        :param index:
        :return:
        """
        obj = await self._get_from_cache_by_id(id_, index)
        if not obj:
            obj = await self._get_by_id_from_elastic(id_, index)
            if not obj:
                return None
            await self._put_obj_to_cache(obj)
        return obj

    async def search(self, index: str, body: dict) -> Optional[list[Film], list[Person], list[Genre]]:
        """
        Выполняет поиск данных по запросу (body) и индексу. Сначала проверяет наличие данных в кеше.
        Если данных в кеше нет - обращается к эластику и кеширует положительный результат.

        :param index:
        :param body:
        :return:
        """
        docs = await self._get_from_cache_by_body(body, index)
        if not docs:
            docs = await self._search_in_elastic(index=index, body=body)
            if not docs:
                return None
            key = await self._str2md5(body)
            await self._put_obj_to_cache(docs, key=key)

        return docs

    async def _search_in_elastic(self, body: dict, index: str) -> Optional[Film, Person, Genre]:
        """
        Выполяет поиск в индексе эластика index по запросу body.
        Возвращаемый результат валидируется моделью.

        :param body:
        :param index:
        :return:
        """
        docs = await self.elastic.search(index=index, body=body)
        docs = docs.get("hits", {})
        docs = docs.get("hits", [])
        data_model = self.models[index]
        docs = [data_model(**d["_source"]) for d in docs]
        return docs

    async def _get_by_id_from_elastic(self, id_: str, index: str) -> Optional[Film, Person, Genre]:
        """
        Забирает данные из эластика по id. Результат валидируется моделью.

        :param id_:
        :param index:
        :return:
        """
        try:
            doc = await self.elastic.get(index, id_)
            data_model = self.models[index]
            return data_model(**doc["_source"])
        except Exception:
            logger.exception("Ошибка на этапе забора документа из elastic по id")
            return

    async def _get_from_cache_by_id(self, id_: str, index: str) -> Optional[Film, Person, Genre]:
        """
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        # pydantic предоставляет удобное API для создания объекта моделей из json

        :param id_:
        :param index:
        :return:
        """
        data = await self.redis.get(id_)
        if not data:
            return None

        data_model = self.models[index]
        obj = data_model.parse_raw(data)
        return obj

    async def _str2md5(self, body: dict) -> str:
        """
        Возвращает md5 от словаря с запросом к эластику.

        :param body:
        :return:
        """

        return hashlib.md5(str(body).encode("utf-8")).hexdigest()

    async def _get_from_cache_by_body(self, body: dict, index: str) -> Optional[list[Film], list[Person], list[Genre]]:
        """
        Забирает данные из кеша по ключу (body).
        Полученные данные вставляет в модель данных

        :param body:
        :param index:
        :return:
        """
        key = await self._str2md5(body)
        data = await self.redis.get(key)
        if not data:
            return None

        data_model = self.models[index]
        data = json.loads(data)["result"]
        obj = [data_model.parse_raw(d) for d in data]
        return obj

    async def _put_obj_to_cache(
        self,
        obj: Union[Film, Person, Genre, list[Film], list[Person], list[Genre]],
        key: str = None,
    ) -> None:
        """
        Сохраняем данные о фильме, используя команду set
        Выставляем время жизни кеша — 5 минут
        https://redis.io/commands/set
        pydantic позволяет сериализовать модель в json

        :param obj:
        :return:
        """

        if not key:
            key = obj.id
            data_to_cache = obj.json()

        else:
            data_to_cache = json.dumps({"result": [d.json() for d in obj]})

        await self.redis.set(key, data_to_cache, expire=CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
