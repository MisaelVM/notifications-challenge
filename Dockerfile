## ------------------------ Build Stage ------------------------- ##
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY . ./
RUN uv sync --locked --no-dev


## ---------------------- Production Stage ---------------------- ##
FROM python:3.14-slim-trixie AS production

RUN useradd --create-home appuser
USER appuser

WORKDIR /app

COPY --from=builder --exclude=tests/ /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD [ "/bin/sh", "-c", "alembic upgrade head && exec fastapi run --host 0.0.0.0 --port \"$PORT\" --proxy-headers --forwarded-allow-ips '*'"]

## ---------------------- Build-Dev Stage ----------------------- ##
FROM builder AS builder-dev

COPY --from=builder /usr/local/bin/uv /usr/local/bin/uvx /bin/
RUN uv sync --locked

## ------------------------- Test Stage ------------------------- ##
FROM python:3.14-slim-trixie AS test

RUN useradd --create-home appuser
USER appuser

WORKDIR /app

COPY --from=builder-dev /app /app
COPY --from=builder-dev /bin/uv /bin/uvx /bin/
COPY tests ./tests


ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

CMD [ "/bin/sh", "-c", "exec uv run pytest --cov=app --cov-report term-missing --cov-report lcov tests/ -v" ]
