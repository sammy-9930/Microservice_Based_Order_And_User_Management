FROM python:3.12-slim

WORKDIR /app 

COPY api_gateway/ /app/api_gateway 

RUN pip install --no-cache-dir -r api_gateway/requirements.txt

CMD ["uvicorn", "api_gateway.gateway:app", "--host", "0.0.0.0", "--port", "8080"]