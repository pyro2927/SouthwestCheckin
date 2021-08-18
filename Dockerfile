FROM python:3.7
WORKDIR /usr/src/app

COPY . .
RUN pip install .[dev] --no-cache-dir

ENTRYPOINT ["./entrypoint.sh"]
