FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /register
COPY . /register/

RUN pip install -r requirements.txt

EXPOSE 8000
