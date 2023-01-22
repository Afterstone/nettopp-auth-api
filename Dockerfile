FROM python:3.10-slim-buster


WORKDIR /app

RUN \
    adduser --disabled-login nopriv \
    && mkdir -p /app/src/auth_api/ \
    && chown -R nopriv /app
    # Make flit install packages only, to cache package installation.


COPY src/auth_api/__init__.py src/auth_api/__init__.py
COPY \
    pyproject.toml \
    setup.cfg \
    README.md \
    ./
RUN pip install --no-cache-dir . && rm -rf src/

# Add the project source code to the package.
# NB: We have to delete source because Docker complains about
#   multiple versions of folders/files from the previous COPY.
COPY src/ .
RUN pip install --no-cache-dir .

ENV PORT=8000

USER nopriv
CMD [ \
    "bash", "-c", \
    "python -m auth_api.main" \
]
