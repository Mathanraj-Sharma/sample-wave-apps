.PHONY: setup
setup:
	python3 -m venv venv
	./venv/bin/pip install -U pip
	./venv/bin/pip install wheel
	./venv/bin/pip install -r requirements.txt

.PHONY: test
test:
	pytest tests/unit_tests

.PHONY: test-e2e
test-e2e:
	DEBUG=pw:api pytest -s  tests/e2e_tests/


