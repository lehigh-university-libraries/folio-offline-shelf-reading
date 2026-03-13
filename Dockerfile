FROM ghcr.io/lehigh-university-libraries/python3.13:main@sha256:006fa58b9502635a205c2d9b7e17dd7c597f6709d5618558e534443228411054

COPY requirements.txt /app
RUN uv pip install \
   --break-system-packages \
   --system \
   -r /app/requirements.txt

COPY . /app

