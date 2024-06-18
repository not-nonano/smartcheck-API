from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from passlib.context import CryptContext
import uuid, asyncio

# Connect to MongoDB
client = MongoClient(
    "mongodb+srv://NUSMartCheck:QSx4OW0LA2HBG1yl@cluster0.uletfdh.mongodb.net/?retryWrites=true&w=majority")


# Access a specific database
db = client["NUSmartApp"]

# Access a specific collection
collection = db["account"]
collection2 = db["answerkey"]
collection3 = db["applicantlist"]

router = APIRouter()

@router.post("/userValid")
async def username_Valid(request: Request):
    data = await request.json()

    username = data.get("username")

    query = {"username": username}

    result = collection.find_one(query)
    if result:
        return JSONResponse(content={"message": "Found one!", "exist": True}, status_code=200)
    else:
        return JSONResponse(content={"message": "User not found", "exist": False}, status_code=200)


@router.patch("/changePassword")
async def change_password(request: Request):
    data = await request.json()
    password = data.get("password")

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    hashed_password = pwd_context.hash(password)

    query = {"_id": id}

    update = {"$set": {"password": hashed_password,}}
    result = collection.update_one(query, update)

    if result.matched_count > 0:
        return {"message": "User updated successfully"}
    else:
        return {"message": "User not found"}

@router.post("/addUser/v2")
async def v2_add_user(request: Request):
    
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    hashed_password = pwd_context.hash(password)

    user = {
        "_id": str(uuid.uuid4()),
        "username": username,
        "password": hashed_password,
        "role": role
    }

    result = collection.insert_one(user)

    if result.inserted_id:
        return {"message": "User added successfully"}
    else:
        return {"message": "Failed to add user"}

@router.post("/authenticateUser/")
async def authenticate(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    user = collection.find_one({"username": username})

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    if user and pwd_context.verify(password, user["password"]):
        return JSONResponse(content={"message": "Authenticated!", "authenticated": True, "_id": user['_id'] , "username": username, "role": user['role']})
    else:
        return JSONResponse(content={"message": "Authentication Failed!", "authenticated": False})
        


@router.post("/checkUser/")
async def get_user(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    result = collection.find_one({"username": username, "password": password})
    if result:
        return JSONResponse(content=result, status_code=200)
    else:
        return JSONResponse(content={"message": "User not found"}, status_code=404)


@router.post("/addUser/")
async def add_user(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    isActive = data.get("isActive")
    role = data.get("role")

    user = {
        "_id": str(uuid.uuid4()),
        "username": username,
        "password": password,
        "isActive": isActive,
        "role": role
    }
    result = collection.insert_one(user)

    if result.inserted_id:
        return {"message": "User added successfully"}
    else:
        return {"message": "Failed to add user"}


@router.patch("/editUser/")
async def edit_user(request: Request):
    data = await request.json()
    id = data.get("_id")
    password = data.get("password")
    role = data.get("role")

    query = {"_id": id}

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    hashed_password = pwd_context.hash(password)

    update = {"$set": {"password": hashed_password, "role": role}}
    result = collection.update_one(query, update)

    if result.matched_count > 0:
        return {"message": "User updated successfully"}
    else:
        return {"message": "User not found"}


@router.delete("/deleteUser/")
async def delete_user(request: Request):
    data = await request.json()
    id = data.get("_id")

    filter = {"_id": id}
    result = collection.delete_one(filter)

    if result.deleted_count > 0:
        return {"message": "User deleted successfully"}
    else:
        return {"message": "User not found"}


@router.get("/getAllUser/")
def get_all_user():
    result = collection.find()
    return list(result)