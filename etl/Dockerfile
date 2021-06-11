FROM python:3.9
# install certificate for yandex cloud
RUN mkdir -p ~/.postgresql && \
    wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" -O ~/.postgresql/root.crt && \
    chmod 0600 ~/.postgresql/root.crt
# install requirements
WORKDIR /src
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt
# start script
COPY /src .
CMD python -m main