dev: requirements/dev.txt

all: dist/request_review

requirements/base.txt: requirements/base.in
	pip-compile requirements/base.in > requirements/base.txt

requirements/dev.txt: requirements/base.txt requirements/dev.in
	pip-compile requirements/dev.in > requirements/dev.txt

requirements/test.txt: requirements/base.txt requirements/test.in
	pip-compile requirements/test.in > requirements/test.txt

dist/request_review: request_review.py
	pyinstaller -F -s request_review.py

test:
	coverage run -m unittest discover -s tests --verbose
