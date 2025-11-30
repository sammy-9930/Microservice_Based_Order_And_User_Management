FROM python:3.12-slim 

WORKDIR /app 

COPY user_service_v2/ /app/user_service_v2 

RUN pip install --no-cache-dir -r user_service_v2/requirements.txt 

EXPOSE 8000

CMD ["uvicorn", "user_service_v2.main:app", "--host", "0.0.0.0", "--port", "8000"]