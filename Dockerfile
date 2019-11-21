FROM python:latest

COPY . .
RUN pip install pipenv
RUN pipenv install

CMD pipenv run python netecho.py
