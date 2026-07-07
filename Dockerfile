# -------- Base --------
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# skip installing man pages/docs so mandb never has anything to index
RUN echo 'path-exclude /usr/share/man/*' > /etc/dpkg/dpkg.cfg.d/01_nodoc \
 && echo 'path-exclude /usr/share/doc/*' >> /etc/dpkg/dpkg.cfg.d/01_nodoc

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

# create django user
RUN addgroup --system django && adduser --system --ingroup django django

# create necessary directories and set permissions BEFORE switching user
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R django:django /app/staticfiles /app/media \
    && chmod -R 755 /app/staticfiles /app/media

# switch to django user
USER django

EXPOSE 8000

CMD ["gunicorn", "umsproj.asgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]