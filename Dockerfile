# Apify Python actor — pinned base image from last green build (1.1.65)
FROM apify/actor-python:3.12@sha256:7817f0ae3217f6d4f7fc8ce2463240481e3f0b0a313f10793bafbcf5d88398f5

COPY --chown=myuser:myuser requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=myuser:myuser app/ ./app/
COPY --chown=myuser:myuser src/ ./src/
COPY --chown=myuser:myuser refinery_core_src/ ./refinery_core_src/

CMD ["python", "src/main.py"]
