FROM python:3.10

# Configure Poetry
ENV POETRY_VERSION=1.4.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

#RUN apt-get update && \
#    apt-get -qy full-upgrade && \
#    apt-get install -qy curl && \
#    apt-get install -qy curl && \
#    curl -sSL https://get.docker.com/ | sh

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry lock
RUN poetry install

# Run your app
COPY . /app
CMD [ "poetry", "run", "python", "run.py" ]
