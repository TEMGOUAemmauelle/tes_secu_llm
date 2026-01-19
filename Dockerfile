FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Base system
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r /tmp/requirements.txt

# Workspace
WORKDIR /app

COPY . /app

EXPOSE 8000

CMD ["python3", "runner.py"]
