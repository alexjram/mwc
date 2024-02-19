FROM python:3.10-alpine

COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /appdata/www
WORKDIR /appdata/www

CMD python main.py
