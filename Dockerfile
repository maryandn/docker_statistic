FROM python:3.8-alpine

MAINTAINER Me

ENV PYTHONUNBUFFERED 1

COPY ./flussonic_stat/Pipfile /tmp

RUN apk add --no-cache --virtual ..build-deps gcc musl-dev mariadb-dev libffi-dev

RUN pip install --upgrade pip && pip install pipenv
RUN cd /tmp && pipenv lock --requirements > requirements.txt && pip install -r requirements.txt

RUN mkdir /app
RUN mkdir /app/static

WORKDIR /app
COPY flussonic_stat /app

RUN adduser -D user
USER user
