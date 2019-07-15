FROM python:3.6

EXPOSE 50051

WORKDIR /app

ADD ./wait-for-it.sh /app/wait-for-it.sh

ADD ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

ADD ./*.py /app/
ADD ./__init__.py /app/

RUN ["chmod", "+x", "./wait-for-it.sh"]
