FROM python:3.7-slim

LABEL maintainer="Dylan Finn <dylanfinn89@gmail.com>"

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev


# Cache dependencies
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python3", "app.py"]