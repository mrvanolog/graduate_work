FROM python:3
ENV PYTHONUNBUFFERED=1 \
    ES_URL=http://elasticsearch:9200 \
    ETL_FIRST_RUN=True
WORKDIR /src
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY /src .
CMD ["python3", "main.py"]