.PHONY: install run-pipeline run-dashboard test

install:
	pip install -r requirements.txt

run-pipeline:
	python run_pipeline.py

run-dashboard:
	streamlit run dashboard/app.py

test:
	pytest -q
