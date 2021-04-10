FROM jrottenberg/ffmpeg:4.1-alpine


FROM python:3.9-slim


WORKDIR /
RUN pip3 install --no-cache-dir requests==2.25.1

COPY --from=0 /usr/local/ /usr/local
COPY --from=0 /usr/lib/ /usr/lib
COPY --from=0 /lib/ /lib

COPY fetch-source.py /
RUN python3 /fetch-source.py

RUN apt-get update && apt-get install -y fonts-liberation && apt-get clean


COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY main.py /
CMD [ "python3", "/main.py" ]

