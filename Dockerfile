FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY src/ ./src/
COPY refinery_core_src/ ./refinery_core_src/

CMD ["python", "src/main.py"]
