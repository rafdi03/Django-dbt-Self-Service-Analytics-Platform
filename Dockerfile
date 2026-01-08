FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV DBT_PROFILES_DIR=/app/dbt_profiles

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-c", "print('Container is up')"]
