FROM python:slim

RUN groupadd -g 2022 python && \
    useradd -g 2022 -u 2022 --create-home --home-dir /usr/src/app python

USER python
WORKDIR /usr/src/app

ENV PATH="${PATH}:/usr/src/app/.local/bin:/usr/src/app"

COPY Pipfile Pipfile.lock ./

RUN pip install --user pipenv && \
    pipenv install

COPY lib lib
COPY models models
COPY torrentino.py .

RUN mkdir -p ./config
COPY config/torrentino.yaml /usr/src/app/config/torrentino.yaml

ENTRYPOINT [ "pipenv", "run", "./torrentino.py" ]
# ENTRYPOINT [ "/bin/bash"]