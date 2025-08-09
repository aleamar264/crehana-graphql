# Install uv
FROM python:3.13-slim-bullseye AS builder
RUN apt-get update && apt-get upgrade -y && apt-get clean
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

COPY pyproject.toml uv.lock /app/

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.13-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get clean

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY src .
COPY .env .env
# ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://jaeger-collector.monitoring.svc.cluster.local:4318/v1/traces

# Run the application
CMD ["/app/.venv/bin/granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "main:app"]