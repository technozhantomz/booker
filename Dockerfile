FROM python:3.8.3-alpine3.12 as shared

RUN apk upgrade --no-cache && \
    apk add \
    --no-cache \
    libpq \
    libzmq

WORKDIR /booker

COPY requirements-pipenv.txt .

RUN pip3 install \
    --no-cache-dir \
    --user \
    -r requirements-pipenv.txt && \
    rm requirements-pipenv.txt

ENV PATH="${PATH}:/root/.local/bin"

FROM shared as builder

RUN apk add \
    --no-cache \
    pkgconfig \
    libc-dev \
    libffi-dev \
    postgresql-dev \
    zeromq-dev \
    gcc \
    g++

COPY Pipfile.lock ./

RUN pipenv install \
    --clear \
    -d \
    --ignore-pipfile \ 
    --keep-outdated && \
    rm -rf "${HOME}/.cache"

FROM shared as bytecompile

COPY booker booker
COPY tests tests

RUN python3 -m compileall -b booker
RUN python3 -m compileall -b tests

FROM shared

COPY --from=builder /root /root

COPY --from=builder /booker/Pipfile.lock .

COPY alembic.ini .
COPY --from=bytecompile /booker/booker booker
COPY --from=bytecompile /booker/tests tests

COPY conftest.py .

COPY Pipfile .

ARG HTTP_PORT
ENV HTTP_PORT="${HTTP_PORT}"

EXPOSE "${HTTP_PORT}/tcp"

CMD pipenv run migrate && pipenv run serve
