FROM python:3.9

ENV PYTHONPATH=/app/src

WORKDIR /app
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src .
EXPOSE 8000

CMD uvicorn --port 8000 --host 0.0.0.0 main:app