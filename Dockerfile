FROM ghcr.io/lehigh-university-libraries/python3.13:main@sha256:79f6dc7d69c2befaafebb481970dcb1714c4f74cb645494394b99856e3246d3a

COPY requirements.txt /app
RUN uv pip install \
   --break-system-packages \
   --system \
   -r /app/requirements.txt

COPY . /app

