FROM apify/actor-python:3.12

COPY --chown=myuser:myuser requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=myuser:myuser app/ ./app/
COPY --chown=myuser:myuser src/ ./src/
COPY --chown=myuser:myuser refinery_core_src/ ./refinery_core_src/

CMD ["python", "src/main.py"]
