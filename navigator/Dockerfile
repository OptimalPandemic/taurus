FROM python:3.6

EXPOSE 50051

WORKDIR /app


ADD ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

ADD ./*.py /app/
ADD ./__init__.py /app/

CMD python3 main.py