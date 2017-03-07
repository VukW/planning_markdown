FROM python:3.6
MAINTAINER Viacheslav Kukushkin
ADD . /code
# VOLUME ["/app"]
# RUN mkdir /app
WORKDIR /code
RUN pip install -r requirements.txt
CMD python run.py