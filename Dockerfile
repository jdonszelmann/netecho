FROM python:3.7

WORKDIR /app

RUN pip install 'pipenv==2018.11.26' --no-cache-dir

COPY Pipfile* /app/

RUN pipenv install --deploy --system

COPY netecho.py /app/

EXPOSE 8000

ENV NETECHO_PORT 8000
ENV PYTHONBUFFERED 0
CMD hypercorn -b 0.0.0.0 netecho:app
