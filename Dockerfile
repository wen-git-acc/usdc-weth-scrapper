FROM docker-registry.gitlab.myteksi.net/library/python:3.11

# Copy poetry files
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

# install poetry and all dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main

# Copy source code
COPY tests tests
COPY Makefile Makefile
COPY configs configs
COPY scripts scripts
COPY app app

# Run the application
EXPOSE 8088
CMD make run
