FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && \
    pip install --no-cache-dir fastapi sqlalchemy
ENV SECRET_KEY "765e6d6a8fa43f75a5fdd20e31b136b1c6dc2641e2f6646a504353745285f905"
COPY ./app /app
COPY ./start.sh /start.sh
RUN chmod +x /start.sh

