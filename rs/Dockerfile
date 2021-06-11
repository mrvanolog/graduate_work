FROM python:3.9
ENV POSTGRES_USER=user_admin \
    POSTGRES_PASSWORD=qwerty123 \
    POSTGRES_HOST=rc1b-9g35diheb1pr3mvu.mdb.yandexcloud.net \
    POSTGRES_PORT=6432
# install certificate for yandex cloud
RUN mkdir -p ~/.postgresql && \
    wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" -O ~/.postgresql/root.crt && \
    chmod 0600 ~/.postgresql/root.crt
# install requirements
WORKDIR /src
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt
# start a server
COPY /src .
EXPOSE 8080
CMD uvicorn --port 8080 --host 0.0.0.0 main:app