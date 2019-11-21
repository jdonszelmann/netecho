FROM pipenv:latest

COPY . .
RUN pipenv install

CMD pipenv run python netecho.py
