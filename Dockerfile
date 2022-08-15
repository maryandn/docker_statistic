FROM python:3.8-alpine

MAINTAINER Me

ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache --virtual .build-deps gcc musl-dev mariadb-dev

RUN mkdir /app
RUN mkdir /app/static
WORKDIR /app

RUN adduser -D user
ENV PATH="/home/user/.local/bin:${PATH}"
USER user

RUN /usr/local/bin/python -m pip install --upgrade pip && pip install pipenv

COPY ./flussonic_stat/Pipfile /tmp
RUN cd /tmp && pipenv lock --requirements > requirements.txt && pip install -r requirements.txt
