FROM python:3.7-buster

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 7007

CMD [ "python", "-u", "server.py" ]