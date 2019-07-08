FROM python:3.6

EXPOSE 50051

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt
COPY *.py ./
CMD python3 main.py