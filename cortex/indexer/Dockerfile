# Indexer Service
# Indexes Obsidian markdown files into pgvector

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "indexer.py"]
