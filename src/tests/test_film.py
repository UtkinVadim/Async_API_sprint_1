from pprint import pprint
from unittest import TestCase

from fastapi.testclient import TestClient

from main import app


class FilmTestCase(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_get_film(self):  # noqa: E800
        # Параметры запроса в get методе передаются как "params"
        params = {
            "query": "war",
            "page[size]": "2",
            "page[number]": "100",
            "filter[genre]": "120a21cf-9097-479e-904a-13dd7198c1dd",
        }

        # Делаем запрос используя fastapi TestClient. Первый параметер - url.
        response = self.client.get("/api/v1/film/search/", params=params)

        # Проверка, что сервер ответил статусом 200. Пока закомменчу но суть проверок в этом=)
        # assert response.status_code == 200, response.json()  # noqa: E800

        # Ответ от сервера лежит тут
        pprint(response.json())  # noqa: T003
