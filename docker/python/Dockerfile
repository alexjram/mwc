FROM alpine:latest

RUN apk update

RUN mkdir -p /appdata/www
WORKDIR /appdata/www

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add --update py-pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt --break-system-packages

RUN apk add ffmpeg

CMD python3 main.py
