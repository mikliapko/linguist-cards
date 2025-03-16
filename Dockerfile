FROM python:3.13-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

RUN pip install uv --break-system-packages
ENV PATH="/root/.local/bin:$PATH"

COPY uv.lock pyproject.toml /app/
RUN uv venv sync

COPY . /app

ENTRYPOINT ["uv", "run", "python", "bot.py", "-l"]
