from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient, DESCENDING
import uuid
from datetime import datetime
from models.answer_key import Answer_Key, Post_Answer_Key

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

@router.get("/getAnswerKey/")
def get_answer_key():

    result = collection2.find_one(sort=[("date", -1)])
    return result

@router.post("/getFilteredAnswerKey/")
async def get_data(request: Request):

    req = await request.json()

    start_date = req.get("start")
    start_timestamp = datetime.fromisoformat(start_date).timestamp()

    cursor = collection2.find().sort("date", DESCENDING)

    answerKey = {}
    data = list(cursor)
    for doc in data:
        if doc['date'] < start_timestamp:
            answerKey = doc
            break 
    
    if not answerKey:
        answerKey = data[-1]

    return answerKey

@router.patch("/updateAnswerKey/")
async def update_answer_key(request: Request):
    answer_key = await request.json()
    english = answer_key.get("english")
    science = answer_key.get("science")
    mathematics = answer_key.get("mathematics")
    aptitude = answer_key.get("aptitude")

    data = {
            "_id": str(uuid.uuid4()),
            "english": english,
            "science": science,
            "mathematics": mathematics,
            "aptitude": aptitude,
            "date": datetime.now().timestamp()
         }
    result = collection2.insert_one(data)

    if result.inserted_id:
        return {"message": "Answer key updated successfully"}
    else:
        return {"message": "Answer key not found"}
    
@router.patch("/testUpdate/")
async def update_answer_key(answer_key: Answer_Key):
    data = {
        "_id": str(uuid.uuid4()),
        "english": answer_key.english,
        "science": answer_key.science,
        "mathematics": answer_key.mathematics,
        "aptitude": answer_key.aptitude,
        "date": datetime.now().timestamp()
    }
    result = collection2.insert_one(data)

    if result.inserted_id:
        return {"message": "Answer key updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Answer key not found")