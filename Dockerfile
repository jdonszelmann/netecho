FROM python:3.8-alpine

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install
COPY netecho.py .

ENTRYPOINT pipenv run python netecho.py
