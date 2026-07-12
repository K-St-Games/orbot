# RAG MCP Server
# Semantic search over Obsidian notes via MCP protocol

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8100

CMD ["python", "server.py"]
