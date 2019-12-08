FROM python:3.7.5-slim

COPY ./requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

CMD ["gunicorn","wsgi:app", "--workers", "4", "--access-logfile","-","--bind","0.0.0.0:8000"]