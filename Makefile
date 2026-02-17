VENV := .venv
PYTHON := $(VENV)/bin/python
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy
UV := $(VENV)/bin/uv

.PHONY: dev lint run check-venv

check-venv:
	@test -x $(PYTHON) || (echo "❌ Virtualenv not found. Run: uv sync" && exit 1)

dev:
	uv sync --extra dev

lint: check-venv
	$(RUFF) format .
	$(RUFF) check .

run-extract: check-venv
	$(PYTHON) -m dataset_extractor.cli --input data/raw/$(PDF) --output data/processed/Extracted_$(PDF)

run-norm: check-venv
	@test -n "$(CSV)" || (echo "❌ CSV is required: make run-norm CSV=Building_Permits.csv" && exit 1)
	$(PYTHON) -m address_normalizer.cli --input data/raw/$(CSV) --output data/processed/Normalized_$(CSV)

run-geo: check-venv
	@test -n "$(CSV)" || (echo "❌ CSV is required: make run-geo CSV=Normalized_Building_Permits.csv" && exit 1)
	$(PYTHON) -m dataset_geocoder.cli --input data/processed/$(CSV) 

