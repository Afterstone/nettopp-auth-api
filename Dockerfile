FROM python:3.10-slim-buster

WORKDIR /app

# Make flit install packages only, to cache package installation.
RUN mkdir -p /app/src/auth_api/
COPY src/auth_api/__init__.py src/auth_api/__init__.py
COPY \
    pyproject.toml \
    setup.cfg \
    README.md \
    ./
RUN pip install .

# Add the project source code to the package.
COPY . .
RUN pip install .

ENV PORT=8000
CMD [ \
    "bash", "-c", \
    "python -m auth_api.main" \
]
