FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir fastapi sqlalchemy
COPY ./app /app
