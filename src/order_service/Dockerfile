# Use an official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

COPY order_service/ /app/order_service

RUN pip install --no-cache-dir -r order_service/requirements.txt

# Expose service port
EXPOSE 8000 

# Run the FastAPI app
CMD ["uvicorn", "order_service.main:app", "--host", "0.0.0.0", "--port", "8000"]

