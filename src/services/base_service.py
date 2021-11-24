import hashlib
import json
import logging
from typing import List, Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel

from core.config import CACHE_EXPIRE_IN_SECONDS

logger = logging.getLogger(__name__)


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = None
        self.model = None

    async def get_by_id(self, id_: str, index: str = None) -> Optional[BaseModel]:
        """
        Возвращает объект по id из указанного индекса. Сначала ищет объект в кеше,
        при отсутствии: берёт из базы, кладёт в кеш, возвращает найденный объект.

        :param id_:
        :param index:
        :return:
        """
        obj = await self._get_from_cache_by_id(id_)
        if not obj:
            index = index if index else self.index
            obj = await self._get_by_id_from_elastic(id_, index)
            if not obj:
                return None
            await self._put_obj_to_cache(obj)
        return obj

    async def search(self, body: dict) -> Optional[List[BaseModel]]:
        """
        Выполняет поиск данных по запросу (body) и индексу. Сначала проверяет наличие данных в кеше.
        Если данных в кеше нет - обращается к эластику и кеширует положительный результат.

        :param body:
        :return:
        """
        docs = await self._get_from_cache_by_body(body)
        if not docs:
            docs = await self._search_in_elastic(body=body)
            if not docs:
                return None
            key = await self._str2md5(body)
            await self._put_obj_to_cache(docs, key=key)

        return docs

    async def _search_in_elastic(self, body: dict) -> Optional[List[BaseModel]]:
        """
        Выполяет поиск в индексе эластика index по запросу body.
        Возвращаемый результат валидируется моделью.

        :param body:
        :return:
        """
        docs = await self.elastic.search(index=self.index, body=body)
        docs = docs.get("hits", {})
        docs = docs.get("hits", [])
        docs = [self.model(**data["_source"]) for data in docs]
        return docs

    async def _get_by_id_from_elastic(self, id_: str, index: str = None) -> Optional[BaseModel]:
        """
        Забирает данные из эластика по id. Результат валидируется моделью.

        :param id_:
        :return:
        """
        try:
            index = index if index else self.index
            doc = await self.elastic.get(self.index, id_)
            return self.model(**doc["_source"])
        except Exception as err:
            logger.exception(f"Ошибка на этапе забора документа из elastic по id: {err}")
            return

    async def _get_from_cache_by_id(self, id_: str) -> Optional[BaseModel]:
        """
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        # pydantic предоставляет удобное API для создания объекта моделей из json

        :param id_:
        :return:
        """
        data = await self.redis.get(id_)
        if not data:
            return None

        obj = self.model.parse_raw(data)
        return obj

    @staticmethod
    async def _str2md5(body: dict) -> str:
        """
        Возвращает md5 от словаря с запросом к эластику.

        :param body:
        :return:
        """

        return hashlib.md5(str(body).encode("utf-8")).hexdigest()

    async def _get_from_cache_by_body(self, body: dict) -> Optional[List[BaseModel]]:
        """
        Забирает данные из кеша по ключу (body).
        Полученные данные вставляет в модель данных

        :param body:
        :return:
        """
        key = await self._str2md5(body)
        data = await self.redis.get(key)
        if not data:
            return None

        data = json.loads(data)["result"]
        obj = [self.model.parse_raw(d) for d in data]
        return obj

    async def _put_obj_to_cache(
        self,
        obj: Union[BaseModel, List[BaseModel]],
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
