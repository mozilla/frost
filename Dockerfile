# frost

FROM python:3.8-slim-buster

ENV PYTHONPATH $PYTHONPATH:/app
ENV PYTHONUNBUFFERED 1

RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid 10001 --shell /usr/sbin/nologin app
RUN install -o app -g app -d /var/run/depobs /var/log/depobs

# git for herokuadmintools
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
        apt-get upgrade -y && \
        apt-get install --no-install-recommends -y \
            ca-certificates \
            curl \
            git \
            jq

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY * /app/

USER app
ENTRYPOINT [ ]
