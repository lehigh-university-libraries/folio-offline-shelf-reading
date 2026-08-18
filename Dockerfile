FROM ghcr.io/lehigh-university-libraries/python3.13:main@sha256:7c88dae67c6b8dedd419d2620ce6f7d5b6bf33c9cacd8700e6d5dd810ab8c0bd

COPY requirements.txt /app
RUN uv pip install \
   --break-system-packages \
   --system \
   -r /app/requirements.txt

COPY . /app

