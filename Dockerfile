FROM python:slim

WORKDIR /usr/src/app
RUN useradd --home-dir /usr/src/app python && chown python:python /usr/src/app
USER python

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./torrentino.py" ]
