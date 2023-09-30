FROM python:3.8

RUN pip install Flask redis Flask-Session

COPY . /app
WORKDIR /app

CMD ["flask", "run", "--host=0.0.0.0"]
