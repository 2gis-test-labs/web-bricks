.PHONY: deps
deps:
	python3 -m pip install -r requirements.txt

.PHONY: dev-deps
dev-deps:
	python3 -m pip install -r requirements-dev.txt

.PHONY: all-deps
all-deps: deps dev-deps

.PHONY: test-coverage
test-coverage:
	#python3 -m pip install -r requirements-dev.txt
	python3 -m pytest tests/units/ -v --tb=long -l --color=yes --cov=web_bricks --cov-report=term

.PHONY: test-units
test-units:
	#python3 -m pip install -r requirements.txt
	#python3 -m pip install -r requirements-dev.txt
	python3 -m pytest tests/units/ -v --tb=long -l --color=yes

.PHONY: test-imports
test-imports:
	#python3 -m pip install -r requirements-dev.txt
	python3 -m isort web_bricks tests --check-only

.PHONY: test-style
test-style:
	#python3 -m pip install -r requirements-dev.txt
	python3 -m flake8 web_bricks tests

.PHONY: test-all
test-all:
	$(MAKE) test-style
	$(MAKE) test-imports
	$(MAKE) test-unit
	$(MAKE) test-coverage
