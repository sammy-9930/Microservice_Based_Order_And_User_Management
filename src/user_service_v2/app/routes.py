import uuid 
import re 
from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timezone
from user_service_v2.app.models import UserModel
from user_service_v2.app.config import logger
from user_service_v2.app.events import publish_user_update_event

router = APIRouter()

def is_valid_email(email : str):
    try:
        validate_email(email)
        return True 
    except EmailNotValidError:
        return False

def serialize_user(user):
    if not user:
        return None 
    user["_id"] = str(user["_id"])
    return user 

@router.post("/")
async def create_user(request: Request, user: UserModel):
    """Creates a new user"""
    logger.info("Received request to create new user")

    # validate if user already exists in the database 
    users_collection = request.app.users_collection
    existing = users_collection.find_one({"emails" : {"$in" : user.emails}})
    if existing:
        logger.warning(f"user creation failed. Duplicate email found: {user.emails}")
        raise HTTPException(status_code=400, detail="One or more email addresses are already in use")

    user_dict = jsonable_encoder(user)

    # assign a userId 
    user_dict["userId"] = str(uuid.uuid4())
    logger.info(f"Generated new userId = {user_dict['userId']} for user creation")

    #validate email address 
    emailList = user_dict["emails"]
    for email in emailList:
        if not is_valid_email(email):
            raise HTTPException(status_code=400, detail=f"Invalid email address {email}")
        
    user_dict["createdAt"] = datetime.now(timezone.utc)
    user_dict["updatedAt"] = datetime.now(timezone.utc)
        
    # insert user details into database 
    # validate if document is present in DB 
    inserted_id = users_collection.insert_one(user_dict).inserted_id 
    created_user = users_collection.find_one({"_id" : ObjectId(inserted_id)})

    logger.info(f"User created successfully with userId = {user_dict['userId']}")
    return {"status" : "success", "user" : serialize_user(created_user)}

@router.put("/{id}")
async def update_user(id: str, request: Request, data: dict):
    """Allows only emails and deliveryAddress updates"""
    logger.info(f"Received update request for userId={id} with fields={list(data.keys())}")

    users_collection = request.app.users_collection

    # validate the fields being modified 
    allowed = {"emails", "deliveryAddress"}

    for key in data:
        if key not in allowed:
            logger.warning(f"Rejected invalid update field '{key}' for userId={id}")
            raise HTTPException(status_code=400, detail=f"Invalid field: {key}")
        
    if not any(k in data for k in allowed):
        logger.warning(f"No valid fields found in update request for userId={id}")
        raise HTTPException(status_code=400, detail="Either 'emails' or 'deliveryAddress' is required")
    
    old_user = users_collection.find_one({"userId" : id})
    if not old_user:
        logger.error(f"User not found for update request. userId={id}")
        raise HTTPException(status_code=400, detail=f"User not found")
    
    if "emails" in data:
        emails = data["emails"]

        for email in emails:
            if not is_valid_email(email):
                raise HTTPException(status_code=400, detail=f"Invalid email address {email}")
    
    # update timestamp
    data["updatedAt"] = datetime.now(timezone.utc)
    
    users_collection.update_one({"userId" : id}, {"$set" : data})
    new_user = users_collection.find_one({"userId" : id})  
    logger.info(f"User {id} updated successfully. Publishing update event...")

    try:
        publish_user_update_event(id, new_user["emails"], new_user["deliveryAddress"])
        logger.info(f"Published user update event successfully for userId : {id}")
    except Exception as e:
        logger.error(f"Failed to publish user update event for userId {id} : {e}")

    return {
        "status" : "success",
        "after" : serialize_user(new_user),
    }
    