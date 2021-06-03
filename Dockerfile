ARG PY_VERSION=3-slim
FROM python:$PY_VERSION
LABEL maintainer="AskAnna"

# Add repo to /app
ADD . /app
WORKDIR /app

# Set Environment Variables
ENV LIBRARY_PATH=/lib:/usr/lib
ENV PATH /root/.yarn/bin:$PATH
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    g++ \
    tzdata

RUN pip install -U pip \
    && rm -rf /root/.cache

RUN pip install .

RUN rm -rf /app

# Set working directory
WORKDIR /code
