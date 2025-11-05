FROM ghcr.io/lehigh-university-libraries/python3.13:main@sha256:8020c98755e52591b45663ae68d5862e76c892eb4ec91316941bb23c54f3c229

COPY requirements.txt /app
RUN uv pip install --system --no-cache-dir -r /app/requirements.txt

COPY . /app

