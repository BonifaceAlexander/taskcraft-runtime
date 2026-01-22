.PHONY: install test run clean

install:
	pip install -e .
	pip install google-genai pytest pytest-asyncio

test:
	PYTHONPATH=src pytest tests/

run:
	PYTHONPATH=src python -m taskcraft.main_cli run -f examples/desktop_worker.yaml

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache
	find . -name "__pycache__" -type d -exec rm -rf {} +
