# -------- Base --------
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
COPY ams-proj/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy project
COPY ams-proj/ .

# -------- Production --------
FROM base AS production

RUN addgroup --system django && adduser --system --ingroup django django
USER django

EXPOSE 8000

CMD ["gunicorn", "umsproj.asgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]