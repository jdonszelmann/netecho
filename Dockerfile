FROM python:3.7

COPY Pipfile .
COPY Pipfile.lock .
RUN apt-get install gcc -y && \
    pip install quart --no-cache-dir && \
    apt-get remove gcc -y && apt-get clean -y


COPY netecho.py .

CMD python -u netecho.py
