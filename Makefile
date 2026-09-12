.PHONY: help install load run test comment all docker-build docker-up docker-down docker-shell docs

help:
	@echo "Available targets:"
	@echo "  install       Install Python dependencies"
	@echo "  load          Download stock prices and load into Snowflake"
	@echo "  run           Run all dbt models"
	@echo "  test          Run all dbt tests"
	@echo "  comment       Generate AI commentary via Groq and load into Snowflake"
	@echo "  all           Run the full pipeline (load -> run -> test -> comment)"
	@echo "  docs          Generate and serve dbt documentation"
	@echo "  docker-build  Build the Docker image"
	@echo "  docker-up     Start the Docker container in the background"
	@echo "  docker-down   Stop and remove the Docker container"
	@echo "  docker-shell  Open a shell inside the running container"

install:
	pip install -r requirements.txt

load:
	python scripts/load_data.py

run:
	dbt run

test:
	dbt test

comment:
	python scripts/generate_commentary.py

all: load run test comment

docs:
	dbt docs generate
	dbt docs serve

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-shell:
	docker compose exec pipeline bash