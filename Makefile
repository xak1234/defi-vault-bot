install:
	pip install -r requirements.txt

build:
	@echo "No build step needed for serverless function"

start:
	python api/update.py
