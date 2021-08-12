FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV LISTEN_PORT 5000
EXPOSE 5000

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./ltss /app/ltss
COPY ./config /app/config

COPY ./deploy/uwsgi.ini /app/uwsgi.ini