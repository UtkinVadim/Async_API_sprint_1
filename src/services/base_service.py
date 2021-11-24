import json
import logging
from http import HTTPStatus
from typing import List, Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import HTTPException
from pydantic import BaseModel

from core.config import CACHE_EXPIRE_IN_SECONDS

from .utils import flatten_json

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
        key = await self._generate_redis_key(self.index, id_)
        obj = await self._get_from_cache_by_id(key)
        if not obj:
            index = index if index else self.index
            obj = await self._get_by_id_from_elastic(id_, index)
            if not obj:
                return None
            await self._put_obj_to_cache(obj, key=key)
        return obj

    async def search(self, body: dict) -> Optional[List[BaseModel]]:
        """
        Выполняет поиск данных по запросу (body) и индексу. Сначала проверяет наличие данных в кеше.
        Если данных в кеше нет - обращается к эластику и кеширует положительный результат.

        :param body:
        :return:
        """
        key = await self._generate_redis_key(self.index, body)
        docs = await self._get_from_cache_by_body_key(key)
        if not docs:
            docs = await self._search_in_elastic(body=body)
            if not docs:
                return None
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
        except NotFoundError as err:
            logger.exception(f"Ошибка на этапе забора документа из elastic по id: {err}")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=err.info)
        except Exception as err:
            logger.warning(err, exc_info=True)
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err)

    async def _get_from_cache_by_id(self, key: str) -> Optional[BaseModel]:
        """
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        # pydantic предоставляет удобное API для создания объекта моделей из json

        :param key:
        :return:
        """
        data = await self.redis.get(key)
        if not data:
            return None

        obj = self.model.parse_raw(data)
        return obj

    @staticmethod
    async def _generate_redis_key(index: str, body: Union[dict, str]) -> str:
        """
        Создаёт ключ для редиса, по которому будут храниться данные.
        Структура ключа:
        <es_index>::<first_key>::<first_value>::<second_key>::<second_value>

        :param index:
        :param body:
        :return:
        """

        body_list = await flatten_json(body)
        keys_list = [index, *body_list]
        separate_symbol = "::"
        key = separate_symbol.join(keys_list)

        return key

    async def _get_from_cache_by_body_key(self, key: str) -> Optional[List[BaseModel]]:
        """
        Забирает данные из кеша по ключу (body).
        Полученные данные вставляет в модель данных

        :param body:
        :return:
        """
        data = await self.redis.get(key)
        if not data:
            return None

        data = json.loads(data)["result"]
        obj = [self.model.parse_raw(d) for d in data]
        return obj

    async def _put_obj_to_cache(
        self,
        obj: Union[BaseModel, List[BaseModel]],
        key: str,
    ) -> None:
        """
        Сохраняем данные о фильме, используя команду set
        Выставляем время жизни кеша — 5 минут
        https://redis.io/commands/set
        pydantic позволяет сериализовать модель в json

        :param obj:
        :return:
        """

        if isinstance(obj, list):
            data_to_cache = json.dumps({"result": [d.json() for d in obj]})
        else:
            data_to_cache = obj.json()

        await self.redis.set(key, data_to_cache, expire=CACHE_EXPIRE_IN_SECONDS)
