FROM python:3.11.4-alpine

WORKDIR /usr/src/app

# RUN useradd -ms /bin/bash celery

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip 

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

COPY ./worker-entrypoint.sh /usr/src/app/worker-entrypoint.sh

COPY . /usr/src/app/

# RUN chown -R celery:celery /app

# USER celery

RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]
RUN ["chmod", "777", "/usr/src/app/worker-entrypoint.sh"]
RUN ["chmod", "777", "/usr/src/app/mqtt-entrypoint.sh"]
# RUN ["chmod", "777", "/usr/src/app/db.sqlite3"]

# ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]
  