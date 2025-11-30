import json
import random
import logging
import httpx
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_gateway")

app = FastAPI()

# -----------------------------------
# Load routing percentage P
# -----------------------------------
def load_config():
    base_path = os.path.dirname(__file__)
    config_path = os.path.join(base_path, "config.json")
    with open(config_path) as f:
        return json.load(f)


# -----------------------------------
# API Gateway (NO AUTHORIZATION)
# -----------------------------------
@app.middleware("http")
async def gateway_router(request: Request, call_next):

    # Allow gateway's own docs
    if request.url.path in ["/docs", "/openapi.json"]:
        return await call_next(request)

    path = request.url.path

    # 1️⃣ Route ORDER SERVICE directly
    if path.startswith("/orders"):
        backend = "http://order_service:8000"
        chosen = "order-service"
    else:
        # 2️⃣ Weighted routing for USER SERVICE (Strangler Pattern)
        P = load_config().get("P", 50)
        hit = random.randint(1, 100)

        if hit <= P:
            backend = "http://user_service_v1:8000"
            chosen = "v1"
        else:
            backend = "http://user_service_v2:8000"
            chosen = "v2"

    logger.info(f"[ROUTING] → {chosen} | path={path}")

    # Construct backend URL
    url = backend + path
    if request.url.query:
        url += "?" + request.url.query

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                request.method,
                url,
                headers=request.headers.raw,
                content=await request.body()
            )
    except Exception as e:
        logger.error(f"Backend request failed: {e}")
        return JSONResponse({"error": "Backend unavailable"}, status_code=503)

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response.headers
    )
