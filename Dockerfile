FROM python:latest

RUN pip install pipenv
RUN pipenv install
COPY . .

ENTRYPOINT pipenv run python netecho.py
