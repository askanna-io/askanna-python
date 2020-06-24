ARG PY_VERSION=3-slim
FROM python:$PY_VERSION
MAINTAINER AskAnna

# Add repo to /code/
ADD . /code/

# Set working directory.
WORKDIR /code

# Set Environment Variables
ENV LIBRARY_PATH=/lib:/usr/lib
ENV PATH /root/.yarn/bin:$PATH
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip

RUN pip install -U pip \
    && pip install -r requirements_dev.txt \
    && rm -rf /root/.cache

RUN python setup.py install