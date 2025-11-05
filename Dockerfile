FROM python:3.14-bookworm@sha256:e392e288e977be19c14f075d3ec056b9a24113741ead2fcf5e4f3b3009285581

WORKDIR /app

# renovate: datasource=repology depName=debian_12/gosu
ARG GOSU_VERSION="1.14-1+b10"
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    gosu="${GOSU_VERSION}" \
  && rm -rf /var/lib/apt/lists/* \
  && groupadd -r nobody \
  && useradd -r -g nobody pyapp \
  && chown pyapp /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt

ENV FLASK_APP=ShelfReading \
    MODEL_PATH=/app/models \
    ADDRESS=0.0.0.0 \
    PORT=8080 \
    WORKERS=4 \
    SCRIPT_NAME=/

COPY . /app

ENTRYPOINT ["/app/docker-entrypoint.sh"]

HEALTHCHECK CMD curl -f http://localhost:${PORT}${SCRIPT_NAME}healthcheck
