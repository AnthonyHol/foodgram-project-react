FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt ./

RUN pip install --upgrade pip
RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY backend/ ./

EXPOSE 8000

CMD ["sh", "start.sh"]
