FROM python:3.6

EXPOSE 50051

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY *.py /app
CMD python main.py