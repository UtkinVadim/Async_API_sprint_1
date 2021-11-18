run:
	cd src && python main.py

init:
	pip install -r requirements/dev.txt
	pre-commit install
	docker-compose up --build redis -d
	docker-compose up --build elasticsearch -d
