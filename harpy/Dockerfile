FROM python:latest

COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install --upgrade pip
RUN pip install -r requirements.pip

CMD python harpy.py
