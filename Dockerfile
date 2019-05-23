FROM python:3.7

ENV PYTHONPATH="$PYTHONPATH:/app"

RUN pip install pipenv

COPY . /app
WORKDIR /app
RUN pipenv install --system

EXPOSE 8000
CMD gunicorn api.main:app

# TODO gunicorn config file (workers and such)
