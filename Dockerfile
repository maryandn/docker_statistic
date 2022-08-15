FROM python:3.8-alpine

MAINTAINER Me

ENV PYTHONUNBUFFERED 1

COPY ./flussonic_stat/Pipfile /tmp
COPY ./flussonic_stat/Pipfile.lock /tmp

RUN apk add --no-cache --virtual ..build-deps gcc musl-dev mariadb-dev libffi-dev

RUN python -m pip install --upgrade pip && pip install pipenv
RUN cd /tmp && pipenv install --dev --system --deploy

RUN mkdir /app
RUN mkdir /app/static

WORKDIR /app
COPY flussonic_stat /app
RUN adduser -D user
USER user
