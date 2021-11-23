# Async API Team 6
___
**[Ссылка на репозиторий ETL](https://github.com/UtkinVadim/ETL)**
___

### Разворачивание приложения

Для первого запуска выполнить: `make first_time`
последовательность операций:
1. В каталог `_tmp` в текущем репозитории клонируется ETL репозиторий
2. Выполняются команды копирования env и наполнения базы, поднимается контейнер
3. Копируется env и поднимаются контейнеры ETL (elastic и контейнер с кодом ETL)
4. Копируется env для fastapi, поднимаются контейнеры c redis и кодом самого api.

Для последующих: `make chill`
при этом просто поднимутся все необходимые контейнеры

### Горшочек не вари! (Остановка сервиса)
Остановить сервис можно выполнив `make stop`, контейнеры будут остановлены.

Удалить сервис можно выполнив `make down` при этом будут снесены все контейнеры и относящиеся к ним сети и разделы.
Удалить сервис и каталог `_tmp`  можно выполнив `make clean_all`

### Проверка выдачи
**После запуска нужно подождать ~10 секунд пока данные заливаются**
#### через браузер
[http://127.0.0.1:8000/api/openapi](http://127.0.0.1:8000/api/openapi)

#### через терминал

* `curl -L 'http://127.0.0.1:8000/api/v1/film/search/?query='war'&page\[size\]=2&page\[number\]=100&filter\[genre\]=120a21cf-9097-479e-904a-13dd7198c1dd`
* `curl -L 'http://127.0.0.1:8000/api/v1/film/32c9b3b7-4d42-4145-9ca1-47af745df2a1'`
* `curl -L 'http://127.0.0.1:8000/api/v1/film?page\[size\]=2&page\[number\]=100&filter\[genre\]=120a21cf-9097-479e-904a-13dd7198c1dd'`

### Разработка
- Python version: 3.9.7

1. Создать .env файл, при необходимости настроить.
```console
cp .env.template .env
```
2. Инициализировать приложение.
```console
make init
```
*При инициализации будут выполнены следующие действия:*
- Установлены зависимости.
- Установлен pre-commit.
- Поднят контейнер с redis.
- Поднят контейнер с elasticsearch.
4. Запустить сервер.
```console
make run
```
