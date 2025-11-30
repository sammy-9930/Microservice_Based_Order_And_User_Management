import uuid
from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timezone
from order_service.app.models import OrderModel
from order_service.app.config import logger

router = APIRouter()

def serialize_order(order):
    order["_id"] = str(order["_id"])
    return order

@router.post("/")
async def create_order(request: Request, order: OrderModel):
    logger.info(f"Creating order for user {order.userId}")
    orders_collection = request.app.orders_collection
    order_dict = jsonable_encoder(order)

    order_dict["orderId"] = str(uuid.uuid4())

    if "orderStatus" not in order_dict or order_dict["orderStatus"] not in ["under process", "shipping", "delivered"]:
        logger.warning("Invalid or missing orderStatus in request.")
        raise HTTPException(status_code=400, detail="Invalid or missing orderStatus")
    
    order_dict["createdAt"] = datetime.now(timezone.utc)
    order_dict["updatedAt"] = datetime.now(timezone.utc)

    inserted_id = orders_collection.insert_one(order_dict).inserted_id
    created_order = orders_collection.find_one({"_id": ObjectId(inserted_id)})
    created_order["_id"] = str(created_order["_id"])
    logger.info(f"Order created successfully with ID {created_order['orderId']}")
    return {"status": "success", "order": serialize_order(created_order)}

@router.get("/")
async def get_orders(request: Request, status: str):
    logger.info(f"Fetching orders with status '{status}'")
    if status not in ["under process", "shipping", "delivered"]:
        logger.warning(f"Invalid order status requested: {status}")
        raise HTTPException(status_code=400, detail="Invalid status")
    orders_collection = request.app.orders_collection
    orders = list(orders_collection.find({"orderStatus": status}))
    logger.info(f"Found {len(orders)} orders with status '{status}'")
    for o in orders:
        o["_id"] = str(o["_id"])
    return {"status": "success", "orders": orders}

@router.put("/{id}/status")
async def update_order_status(id: str, request: Request, data: dict):
    logger.info(f"Updating order status for orderId={id}")
    orders_collection = request.app.orders_collection

    if "orderStatus" not in data or data["orderStatus"] not in ["under process", "shipping", "delivered"]:
        logger.warning("Invalid or missing orderStatus field.")
        raise HTTPException(status_code=400, detail="Invalid or missing orderStatus")
    
    old_order = orders_collection.find_one({"orderId": id})
    if not old_order:
        logger.error(f"Order not found: {id}")
        raise HTTPException(status_code=404, detail="Order not found")
    
    data["updatedAt"] = datetime.now(timezone.utc)
    
    orders_collection.update_one({"orderId": id}, {"$set": {"orderStatus": data["orderStatus"]}})
    new_order = orders_collection.find_one({"orderId": id})
    logger.info(f"Order {id} status updated successfully to '{data['orderStatus']}'")
    return {"status": "success", "after": serialize_order(new_order)}

@router.put("/{id}/details")
async def update_order_details(id: str, request: Request, data: dict):
    logger.info(f"Updating order details for orderId={id}")

    orders_collection = request.app.orders_collection
    allowed = {"emails", "deliveryAddress"}
    for k in data:
        if k not in allowed:
            logger.warning(f"Invalid field in request: {k}")
            raise HTTPException(status_code=400, detail=f"Invalid field: {k}")
        
    if not any(k in data for k in allowed):
        logger.warning("No valid fields provided in request.")
        raise HTTPException(status_code=400, detail="Either userEmails or deliveryAddress is required")
    
    old_order = orders_collection.find_one({"orderId": id})
    if not old_order:
        logger.error(f"Order not found: {id}")
        raise HTTPException(status_code=404, detail="Order not found")
    
    data["updatedAt"] = datetime.now(timezone.utc)
    
    orders_collection.update_one({"orderId": id}, {"$set": data})
    new_order = orders_collection.find_one({"orderId": id})
    logger.info(f"Order {id} details updated successfully.")
    return {"status": "success", "before": serialize_order(old_order), "after": serialize_order(new_order)}
