.PHONY: help migrate test run docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make migrate    - Run database migrations"
	@echo "  make test       - Run tests"
	@echo "  make run        - Run development server"
	@echo "  make docker-up  - Start Docker containers"
	@echo "  make docker-down - Stop Docker containers"

migrate:
	python manage.py makemigrations
	python manage.py migrate

test:
	pytest

run:
	python manage.py runserver

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down



