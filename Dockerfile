FROM python:latest

COPY Pipfile .
COPY Pipfile.lock .
RUN pip install pipenv
RUN pipenv install
COPY netecho.py .

ENTRYPOINT pipenv run python netecho.py
