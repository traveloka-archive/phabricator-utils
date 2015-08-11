dev: requirements/dev.txt

all: dist/request_review

requirements/base.txt: requirements/base.in
	pip-compile requirements/base.in > requirements/base.txt

requirements/dev.txt: requirements/base.txt requirements/dev.in
	pip-compile requirements/dev.in > requirements/dev.txt

dist/request_review: request_review.py
	pyinstaller -F -s request_review.py

test:
	python -m unittest discover -s tests --verbose
