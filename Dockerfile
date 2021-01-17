FROM python:3.9-alpine

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
EXPOSE 1337

ENTRYPOINT ["python3", "src/start.py"]