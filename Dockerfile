FROM ghcr.io/lehigh-university-libraries/python3.13:main@sha256:9d273ce898a02b5e8f96fca8016e56ef67546bdf8bb39a98438477845ea7e528

COPY requirements.txt /app
RUN uv pip install \
   --break-system-packages \
   --system \
   -r /app/requirements.txt

COPY . /app

