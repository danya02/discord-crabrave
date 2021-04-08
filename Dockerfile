FROM python:slim

RUN pip3 install --no-cache-dir requests==2.25.1
COPY fetch-source.py
RUN python3 fetch-source.py

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY main.py /
CMD [ "python3", "/main.py" ]

