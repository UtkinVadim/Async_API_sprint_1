.PHONY: run_local, local_init, run, clone_etl, run_postgres, run_first_time_ETL, run_first_time_postgres, run_ETL, chill, first_time, clean_all, stop, down, rm_tmp, rm_containers
##### dev automate
run_local:
	python3.9 src/main.py

local_init:
	pip install -r requirements/dev.txt
	pre-commit install
	docker compose up --build

#####
cp_env:
	cp .env.template .env

run:
	docker compose up --build -d

clone_etl:
	mkdir -p _tmp && cd _tmp/ && git clone git@github.com:UtkinVadim/ETL.git

##### Postgres
run_first_time_postgres:
	cd _tmp/ETL/postgres_db && make first_run

run_postgres:
	cd _tmp/ETL/postgres_db && make run

##### ETL
run_first_time_ETL:
	cd _tmp/ETL && make cp_env && make run_etl

run_ETL:
	cd _tmp/ETL && make run_etl


##### Cleaning
stop:
	docker compose stop && \
	cd _tmp/ETL/ && docker compose stop && \
	cd ./postgres_db && docker compose stop

down:
	docker compose down && \
	cd _tmp/ETL/ && docker compose down && \
	cd ./postgres_db && docker compose down

rm_containers:
	docker rm postgres etl elastic fastapi elastic

rm_tmp:
	rm -rf ./_tmp/

##### Clean all
clean_all: down rm_tmp

##### Run all
chill: run_postgres run_ETL run

##### Run all first time
first_time:	clone_etl run_first_time_postgres run_first_time_ETL cp_env run
