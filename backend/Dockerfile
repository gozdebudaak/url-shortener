FROM python:3.12-slim AS builder
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.12.13 /uv /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY app /app/app
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --system --uid 10001 --no-create-home appuser
USER 10001

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]