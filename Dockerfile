from docker.io/python:3.12.13-alpine3.24 as builder

WORKDIR /app

COPY requirements.txt .
RUN python -m venv /venv \
&& /venv/bin/pip install --no-cache-dir -r requirements.txt

from docker.io/python:3.12.13-alpine3.24

WORKDIR /app

RUN addgroup -S analytics-service \
 && adduser -S analytics-service -G analytics-service
USER analytics-service

COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

COPY --chown=analytics-service app.py .
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8005} app:app"]

