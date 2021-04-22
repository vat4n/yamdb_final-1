FROM python:3.8.5

WORKDIR /code

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

RUN ["chmod", "+x", "/code/entrypoint.sh"]

ENTRYPOINT ["/code/entrypoint.sh"]