FROM python:3.8
ENV DOCKER_VERSION='19.03.9'

WORKDIR /tmp/echr_explorer/
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir  -r requirements.txt

RUN set -ex \
    && DOCKER_FILENAME=https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz \
    && curl -L ${DOCKER_FILENAME} | tar -C /usr/bin/ -xzf - --strip-components 1 docker/docker

EXPOSE 8005

CMD [ "python", "./app.py" ]