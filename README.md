# Async API Team 6
___
**[Ссылка на репозиторий ETL](https://github.com/UtkinVadim/ETL)**
___

**Разворачивание приложения**
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
