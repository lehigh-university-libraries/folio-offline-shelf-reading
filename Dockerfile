FROM ghcr.io/lehigh-university-libraries/python3.13:main@sha256:a6033b46e8010fabb8689081f0a174e6ab56fb4feb5322f30569fdbd2cfe9c31

COPY requirements.txt /app
RUN uv pip install \
   --break-system-packages \
   --system \
   -r /app/requirements.txt

COPY . /app

