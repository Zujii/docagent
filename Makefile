.PHONY: setup ingest index ask eval attacks app test
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements-local.txt && pip install -e .
ingest:
	python -m docagent.cli ingest data/raw --parser docling
index:
	python -m docagent.cli index
ask:
	python -m docagent.cli ask "$(Q)"
attacks:
	python -m docagent.eval.attack_gen
eval:
	python -m docagent.eval.run --config evals/default.json
app:
	streamlit run src/docagent/app/streamlit_app.py
test:
	pytest -q
