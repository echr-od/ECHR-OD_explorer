FROM python:3.8
MAINTAINER alexandre.quemy+echr@gmail.com

WORKDIR /tmp/echr_explorer/
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir  -r requirements.txt

EXPOSE 8005

CMD [ "python", "./app.py" ]