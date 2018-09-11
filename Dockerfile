FROM python:3.6

RUN pip install sqlalchemy psycopg2 pytest Flask flask-cors gunicorn gevent requests

WORKDIR /home/app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k gevent", "--reload", "rough.app"]
