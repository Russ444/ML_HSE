FROM python:3.8-slim-buster
RUN mkdir /app
RUN mkdir /app/uploads
COPY . /app/
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["flask_server.py"]
