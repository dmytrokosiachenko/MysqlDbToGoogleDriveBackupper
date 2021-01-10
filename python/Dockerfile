FROM python:3.7-alpine

RUN apk update && \
    apk add gcc musl-dev python3-dev libffi-dev openssl-dev mysql-client && \
    apk add --no-cache mariadb-dev && \
    pip3 install  cryptography --no-binary cryptography pycrypto pyopenssl && \
    apk del gcc musl-dev python3-dev libffi-dev openssl-dev 

# Install bash
#RUN apk add --update bash && rm -rf /var/cache/apk/*

COPY requirements.txt ./

RUN pip3 install -r requirements.txt  

COPY . /usr/src/app
WORKDIR /usr/src/app


CMD [ "python3", "./script.py" ]
