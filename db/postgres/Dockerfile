FROM python:3.9
ENV POSTGRES_USER=user_admin \
    POSTGRES_PASSWORD=qwerty123 \
    POSTGRES_DB=movies \
    POSTGRES_HOST=rc1a-80npisto5z5x0n4n.mdb.yandexcloud.net \
    POSTGRES_PORT=6432
# install certificate for yandex cloud
RUN mkdir -p ~/.postgresql && \
    wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" -O ~/.postgresql/root.crt && \
    chmod 0600 ~/.postgresql/root.crt
# install requirements
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt
# run script
WORKDIR /src
COPY /src .
CMD python -m init_db