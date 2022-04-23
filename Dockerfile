FROM python:3.9-slim

# Disable cache
ENV PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_CREATE=false

# Get dependencies ready
RUN apt-get -y update \
    && apt-get install git netcat -y

# Cleanup
RUN rm -rf /root/.cache/pip/* \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install poetry
RUN pip install poetry

# Define the working directory
WORKDIR /bot

# Install all poetry dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev

# Copy the source files
COPY . .

# Start the container
ENTRYPOINT ["python3"]
CMD ["-m", "bot"]
