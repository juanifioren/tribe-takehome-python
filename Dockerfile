FROM python:3
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade --force-reinstall -r requirements.txt
ADD . /code/
