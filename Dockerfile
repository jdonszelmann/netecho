FROM python:3.7-alpine

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install
COPY netecho.py .

CMD pipenv run python -u netecho.py
