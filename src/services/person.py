import json
import hashlib

from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from core.config import CACHE_EXPIRE_IN_SECONDS


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = "person"

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        doc = await self.elastic.get(self.index, person_id)
        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        film = Person.parse_raw(data)
        return film

    async def search(self, body: dict) -> Optional[List[Person]]:
        persons = await self._get_person_from_cache_by_body(body)
        if not persons:
            persons = await self._search_person_in_elastic(body=body)
            if not persons:
                return
            cache_key = await self._str2md5(body)
            await self._put_list_persons_to_cache(cache_key, persons)
        return persons

    async def _get_person_from_cache_by_body(self, body: dict) -> Optional[List[Person]]:
        key = await self._str2md5(body)
        data = await self.redis.get(key)
        if not data:
            return
        data = json.loads(data)["result"]
        person = [Person.parse_raw(d) for d in data]
        return person

    async def _str2md5(self, body: dict) -> str:
        return hashlib.md5(str(body).encode("utf-8")).hexdigest()

    async def _search_person_in_elastic(self, body: dict) -> Optional[List[Person]]:
        persons_from_es = await self.elastic.search(index=self.index, body=body)
        persons = [Person(**person["_source"]) for person in persons_from_es["hits"]["hits"]]
        return persons

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.id, person.json(), expire=CACHE_EXPIRE_IN_SECONDS)

    async def _put_list_persons_to_cache(self, cache_key: str, persons: List[Person]):
        persons_data = json.dumps({"result": [person.json() for person in persons]})
        await self.redis.set(cache_key, persons_data, expire=CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
