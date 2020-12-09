PYTHON = python3
PIP = ${PYTHON} -m pip
PY_TEST = ${PYTHON} -m pytest


.PHONY: default
default: test lint

.PHONY: deps
deps:
	${PIP} install -e .[dev,mongo,sql,redis]

.PHONY: test
test:
	${PY_TEST}

.PHONY: test-ni
test-ni:
	${PY_TEST} -m "not integration and not sql_integration"

.PHONY: test-i
test-i:
	${PY_TEST} -m "integration"

# SQL integration test runs for Sqlite, MySQL and Postgres
# examples:
# DATABASE_DSN=sqlite:///:memory: make test-sql-i
# DATABASE_DSN=mysql://root:root@localhost/vakt_db ...
# DATABASE_DSN=postgresql+psycopg2://postgres:root@localhost/vakt_db ...
.PHONY: test-sql-i
test-sql-i:
	${PY_TEST} -m "sql_integration"

.PHONY: coverage
coverage:
	${PY_TEST} --cov-config .coveragerc --cov=./ --cov-report html:htmlcov

.PHONY: lint
lint:
	pylint vakt

.PHONY: release
release: test
	${PYTHON} setup.py sdist && ${PYTHON} -m twine upload dist/*

# runs mutation testing
.PHONY: mutation
mutation:
	${PIP} install mutmut
	mutmut run --runner="${PY_TEST}" --paths-to-mutate="vakt/" --dict-synonyms="Struct, NamedStruct"

.PHONY: mutation-report
mutation-report:
	@ruby -e '`mutmut results`.lines.select{ |i| i =~ /\d,/ }.join(",").split(","). \
			 map(&:strip).each { |f| puts " Survived ##{f}"; system "mutmut show #{f}" }'

.PHONY: bench
bench:
	${PYTHON} benchmark.py --checker regex --number 100000
	@echo "\n"
	${PYTHON} benchmark.py --checker rules --number 100000
