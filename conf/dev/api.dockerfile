FROM python:3.12

WORKDIR /app

# install deps from repo's requirements.txt
COPY ./api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt