FROM python:3.6
MAINTAINER Viacheslav Kukushkin
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python run.py