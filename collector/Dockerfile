FROM python:3.6

EXPOSE 50051

WORKDIR /app

COPY requirements.txt ./
COPY *.py ./
COPY __init__.py ./

RUN pip3 install -r requirements.txt

CMD python3 main.py