FROM python:3.6-alpine
MAINTAINER Marek

ENV PYTHONUNBUFFERED 1

COPY ./epg_django/Pipfile /tmp

RUN apk add --no-cache --virtual .build-deps gcc musl-dev mariadb-dev

RUN pip install --upgrade pip && pip install pipenv

RUN mkdir /app
RUN mkdir /app/static
WORKDIR /app
COPY epg_django /app
RUN cd /tmp && pipenv lock --requirements > requirements.txt && pip install -r requirements.txt

RUN adduser -D user
USER user






