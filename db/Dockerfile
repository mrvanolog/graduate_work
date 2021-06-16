FROM python:3.9

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . .
WORKDIR /postgres_rs
CMD ["python3", "init_db.py"]
WORKDIR ../postgres_legacy
CMD ["python3", "init_db.py"]