
ARG python_ver=3.7
FROM python:${python_ver}-slim

ARG nautobot_root=/opt/nautobot
ENV PYTHONUNBUFFERED 1
ENV NAUTOBOT_ROOT ${nautobot_root}

WORKDIR ${NAUTOBOT_ROOT}

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y git && \
    apt-get autoremove -y && \
    apt-get clean all && \
    rm -rf /var/lib/apt/lists/* && \
    pip --no-cache-dir install --upgrade pip wheel

# Upgrade pip and install poetry as well as configure poetry
RUN pip install --upgrade pip\
    && pip install poetry \
    && poetry config virtualenvs.create false

# -------------------------------------------------------------------------------------
# Install Netbox Plugin
# -------------------------------------------------------------------------------------
WORKDIR /source

# Copy in only pyproject.toml/poetry.lock to help with caching this layer if no updates to dependencies
COPY poetry.lock pyproject.toml /source/

# --no-root declares not to install the project package since we're wanting to take advantage of caching dependency installation
# and the project is copied in and installed after this step
RUN poetry install --no-interaction --no-ansi --no-root

# Copy in the rest of the source code and install local Nautobot plugin
COPY . /source
RUN poetry install --no-interaction --no-ansi

# Used if someone wants to override the entrypoint and provision a super user
COPY development/docker-entrypoint.sh /tmp/nautobot/docker-entrypoint.sh

WORKDIR ${NAUTOBOT_ROOT}

ENTRYPOINT ["/tmp/nautobot/docker-entrypoint.sh"]
