FROM python:slim

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY main.py /
CMD [ "python3", "/main.py" ]

