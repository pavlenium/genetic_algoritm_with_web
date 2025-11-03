FROM python:3.12

WORKDIR /app

COPY entrypoint.sh .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir flask[async]
COPY app/ .
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
