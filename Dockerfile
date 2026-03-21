FROM python:2.7-slim

# Fix Debian Buster repositories (EOL)
RUN sed -i s/deb.debian.org/archive.debian.org/g /etc/apt/sources.list && \
    sed -i 's|security.debian.org/debian-security|archive.debian.org/debian-security|g' /etc/apt/sources.list && \
    sed -i '/stretch-updates/d' /etc/apt/sources.list

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    poppler-utils \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    pkg-config \
    python-tk \
    tk-dev \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Upgrade pip to last supported version for 2.7
RUN pip install --upgrade "pip<21.0"

# Pre-install major dependencies (broken pyhrv dependency needs them at build time)
RUN pip install --no-cache-dir \
    numpy==1.16.6 \
    scipy==1.2.3 \
    pandas==0.24.2 \
    matplotlib==2.2.5 \
    biosppy==0.6.1 \
    spectrum==0.7.5 \
    nolds==0.5.2

# Copy requirements and install
COPY app/appsource/requirements_complete.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory to the Django project root (nested by mount)
WORKDIR /app/app/appsource/app_config

# Expose the port used in run.py
EXPOSE 5423

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:5423"]
