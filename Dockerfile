FROM ghcr.io/lehigh-university-libraries/python3.13:main@sha256:cd06431dd7491603b36aa2e12c60959b6b5f39fa008241fbffba5921b6b9443d

COPY requirements.txt /app
RUN uv pip install \
   --break-system-packages \
   --system \
   -r /app/requirements.txt

COPY . /app

