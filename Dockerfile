FROM python:3.10

WORKDIR /app

COPY requirements.txt .
COPY app/ ./app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "/app/app/scraper.py"]

ENV DATABASE_URL="postgresql://postgres:DvzwPPKFUNKULroXcMAHermvOKxMaGRz@postgres.railway.internal:5432/railway"
