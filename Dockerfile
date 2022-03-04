FROM python:3.8

WORKDIR /usr/src/everyservices
COPY . .

EXPOSE 80
VOLUME ["/data"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt



