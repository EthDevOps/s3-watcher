FROM python:3

RUN mkdir /src
WORKDIR /src
RUN pip install boto3 requests

COPY main.py .

CMD ["python","main.py"]
