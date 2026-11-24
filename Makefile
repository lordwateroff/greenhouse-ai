PY ?= .venv/bin/python

setup:            ## create venv and install everything
	python3.12 -m venv .venv && $(PY) -m pip install -r requirements-dev.txt

dev:              ## run the site + API locally (works offline) on http://localhost:8000
	$(PY) -m uvicorn app:app --reload --port 8000

test:
	$(PY) -m pytest -q

cli:
	$(PY) -m greenhouse.cli

experiments:
	$(PY) -m greenhouse.experiments

lint:
	$(PY) -m ruff check .
