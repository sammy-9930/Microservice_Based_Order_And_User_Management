# Use an official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

COPY user_service_v1/ /app/user_service_v1

RUN pip install --no-cache-dir -r user_service_v1/requirements.txt

# Expose service port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "user_service_v1.main:app", "--host", "0.0.0.0", "--port", "8000"]

