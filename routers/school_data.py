from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime


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

@router.post("/getBatchData/")
async def get_batch_data(request: Request):
    
    data = await request.json()
    _id = data.get("_id")
    
    englishCount = {
    "0": [0] * 30,
    "1": [0] * 30,
    "2": [0] * 30,
    "3": [0] * 30,
    "4": [0] * 30,
    "5": [0] * 30
}
    scienceCount = {
    "0": [0] * 30,
    "1": [0] * 30,
    "2": [0] * 30,
    "3": [0] * 30,
    "4": [0] * 30
}
    mathCount = {
    "0": [0] * 30,
    "1": [0] * 30,
    "2": [0] * 30,
    "3": [0] * 30,
    "4": [0] * 30
}
    aptitudeCount = {
    "0": [0] * 30,
    "1": [0] * 30,
    "2": [0] * 30,
    "3": [0] * 30,
    "4": [0] * 30
}
    
    
    result = collection3.find_one({'_id': _id})
    for applicants in result["applicants"]: #applicants
            for index, choice in enumerate(applicants["applicantKeyEnglish"], start=1):
                if isinstance(choice, int):
                    if choice != -1:
                        englishCount[str(choice)][index - 1] += 1
                    else:
                        englishCount["5"][index - 1] += 1
            for index, choice in enumerate(applicants["applicantKeyScience"], start=1):
                if isinstance(choice, int):
                    if choice != -1:
                        scienceCount[str(choice)][index - 1] += 1
                    else:
                        scienceCount["4"][index - 1] += 1
            for index, choice in enumerate(applicants["applicantKeyMathematics"], start=1):
                if isinstance(choice, int):
                    if choice != -1:
                        mathCount[str(choice)][index - 1] += 1
                    else:
                        mathCount["4"][index - 1] += 1
            for index, choice in enumerate(applicants["applicantKeyAptitude"], start=1):
                if isinstance(choice, int):
                    if choice != -1:
                        aptitudeCount[str(choice)][index - 1] += 1
                    else:
                        aptitudeCount["4"][index - 1] += 1

    applicants = [
    {"id": applicant["id"],
     "name": applicant["name"],
     "English": applicant["English"],
     "Mathematics": applicant["Mathematics"],
     "Science": applicant["Science"],
     "Aptitude": applicant["Aptitude"]}
    for applicant in result["applicants"]
]
    
    return {
        "status": "success",
        "proctor": result["proctor"],
        "name": result["name"],
        "englishCount": englishCount,
        "scienceCount": scienceCount,
        "mathCount": mathCount,
        "aptitudeCount": aptitudeCount,
        "applicants": applicants
    }

@router.delete('/deleteApplicantList/')
async def delete_applicant_list(request: Request):
    try:
        request_data = await request.json()
        id = request_data["_id"]
        query = {"_id": id}
        result = collection3.delete_one(query)

        if result.deleted_count > 0:
            return {"message": "Applicant list deleted successfully"}
        else:
            return {"message": "Applicant list not found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getAllApplicantList/")
def get_applicant_list():
    # Retrieve all documents from the collection
    all_data = collection3.find()

    # Process the retrieved data
    results = []
    for data in all_data:
        results.append(data)

    return results


@router.post('/addApplicantList/')
async def add_applicant_list(request: Request):
    request_data = await request.json()
    id = request_data["_id"]
    schoolName = request_data["schoolName"]
    applicants = request_data["applicants"]
    proctor = request_data["proctor"]
    date = request_data["date"]
    archive = request_data["archive"]

    result = collection3.find_one({
        "name": schoolName
    })

    if result:
        return {"status": "success", "duplicate": True}

    collection3.insert_one({
        "_id": id,
        "name": schoolName,
        "applicants": applicants,
        "date": date,
        "proctor": proctor,
        "archive": archive
    })

    return {"status": "success", "duplicate": False}



@router.patch('/editApplicantList/')
async def edit_applicant_list(request: Request):
    try:
        request_data = await request.json()
        id = request_data["_id"]
        archive = request_data["archive"]

        filter = {'_id': id}
        newvalues = {"$set": {'archive': archive}}

        result = collection3.update_one(filter, newvalues)

        if result.matched_count > 0:
            return {"status": "success"}
        else:
            raise HTTPException(
                status_code=404, detail="Applicant list not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getAnalysisData/")
async def get_analysis_data():
    question_count = 30

# Initialize dictionaries to count choices

    englishCount = {
    "0": [0] * question_count,
    "1": [0] * question_count,
    "2": [0] * question_count,
    "3": [0] * question_count,
    "4": [0] * question_count,
    "5": [0] * question_count
}
    mathCount = {
    "0": [0] * question_count,
    "1": [0] * question_count,
    "2": [0] * question_count,
    "3": [0] * question_count,
    "4": [0] * question_count
}
    scienceCount = {
    "0": [0] * question_count,
    "1": [0] * question_count,
    "2": [0] * question_count,
    "3": [0] * question_count,
    "4": [0] * question_count
}
    aptitudeCount = {
    "0": [0] * question_count,
    "1": [0] * question_count,
    "2": [0] * question_count,
    "3": [0] * question_count,
    "4": [0] * question_count
}

    answer_key = collection2.find_one(sort=[("date", -1)])
    answer_key_timestamp = answer_key['date']
    data = list(collection3.find())


    
    for batch in data:
        date_format = "%Y-%m-%d"
        batch_date = datetime.strptime(batch['date'], date_format).timestamp()
        
        if batch_date > answer_key_timestamp:
            for applicants in batch["applicants"]: #applicants
                for index, choice in enumerate(applicants["applicantKeyEnglish"], start=1):
                    if isinstance(choice, int):
                        if choice != -1:
                            englishCount[str(choice)][index - 1] += 1
                        else:
                            englishCount["5"][index - 1] += 1
                for index, choice in enumerate(applicants["applicantKeyScience"], start=1):
                    if isinstance(choice, int):
                        if choice != -1:
                            scienceCount[str(choice)][index - 1] += 1
                        else:
                            scienceCount["4"][index - 1] += 1
                for index, choice in enumerate(applicants["applicantKeyMathematics"], start=1):
                    if isinstance(choice, int):
                        if choice != -1:
                            mathCount[str(choice)][index - 1] += 1
                        else:
                            englishCount["4"][index - 1] += 1
                for index, choice in enumerate(applicants["applicantKeyAptitude"], start=1):
                    if isinstance(choice, int):
                        if choice != -1:
                            aptitudeCount[str(choice)][index - 1] += 1
                        else:
                            aptitudeCount["4"][index - 1] += 1

    return {
        "message": "success",
        "englishCount": englishCount,
        "mathCount": mathCount,
        "scienceCount": scienceCount,
        "aptitudeCount": aptitudeCount,
        }

@router.post("/getFilteredAnalysisData/")
async def get_analysis_data(request: Request):

    data = await request.json()
    start_date = data.get("start")
    end_date = data.get("end")

    query = {
    "date": {"$gte": start_date, "$lte": end_date}
    }

    question_count = 30

# Initialize dictionaries to count choices

    englishCount = {
    "0": [0] * question_count,
    "1": [0] * question_count,
    "2": [0] * question_count,
    "3": [0] * question_count,
    "4": [0] * question_count,
    "5": [0] * question_count
}
    mathCount = {
    "0": [0] * question_count,
    "1": [0] * question_count,
    "2": [0] * question_count,
    "3": [0] * question_count,
    "4": [0] * question_count
}
    scienceCount = {
    "0": [0] * question_count,
    "1": [0] * question_count,
    "2": [0] * question_count,
    "3": [0] * question_count,
    "4": [0] * question_count
}
    aptitudeCount = {
    "0": [0] * question_count,
    "1": [0] * question_count,
    "2": [0] * question_count,
    "3": [0] * question_count,
    "4": [0] * question_count
}

    data = list(collection3.find(query))
    
    for batch in data:
        for applicants in batch["applicants"]: #applicants
            for index, choice in enumerate(applicants["applicantKeyEnglish"], start=1):
                if isinstance(choice, int):
                    if choice != -1:
                        englishCount[str(choice)][index - 1] += 1
                    else:
                        englishCount["5"][index - 1] += 1
            for index, choice in enumerate(applicants["applicantKeyScience"], start=1):
                if isinstance(choice, int):
                    if choice != -1:
                        scienceCount[str(choice)][index - 1] += 1
                    else:
                        scienceCount["4"][index - 1] += 1
            for index, choice in enumerate(applicants["applicantKeyMathematics"], start=1):
                if isinstance(choice, int):
                    if choice != -1:
                        mathCount[str(choice)][index - 1] += 1
                    else:
                        mathCount["4"][index - 1] += 1
            for index, choice in enumerate(applicants["applicantKeyAptitude"], start=1):
                if isinstance(choice, int):
                    if choice != -1:
                        aptitudeCount[str(choice)][index - 1] += 1
                    else:
                        aptitudeCount["4"][index - 1] += 1

    return {
        "message": "success",
        "englishCount": englishCount,
        "mathCount": mathCount,
        "scienceCount": scienceCount,
        "aptitudeCount": aptitudeCount,
        }


# @router.post("/getFilteredDataEnglish/")
# async def get_filtered_data(request: Request):

#     data = await request.json()
#     start_date = data.get("start")
#     end_date = data.get("end")

#     query = {
#     "date": {"$gte": start_date, "$lte": end_date}
#     }

#     question_count = 30

#     englishCount = {
#     "0": [0] * question_count,
#     "1": [0] * question_count,
#     "2": [0] * question_count,
#     "3": [0] * question_count,
#     "4": [0] * question_count
#     }

#     result = list(collection3.find(query))
    
#     for batch in result:
#         for applicants in batch["applicants"]: #applicants
#             for index, choice in enumerate(applicants["applicantKeyEnglish"], start=1):
#                 if isinstance(choice, int):
#                     if choice != -1:
#                         englishCount[str(choice)][index - 1] += 1

#     return {
#         "message": "success",
#         "englishCount": englishCount,
#         }


# @router.get("/getAnalysisDataEnglish/")
# async def get_analysis_data():
#     question_count = 30

# # Initialize dictionaries to count choices
#     englishCount = {
#     "0": [0] * question_count,
#     "1": [0] * question_count,
#     "2": [0] * question_count,
#     "3": [0] * question_count,
#     "4": [0] * question_count
# }

#     data = list(collection3.find())
    
#     for batch in data:
#         for applicants in batch["applicants"]: #applicants
#             for index, choice in enumerate(applicants["applicantKeyEnglish"], start=1):
#                 if isinstance(choice, int):
#                     if choice != -1:
#                         englishCount[str(choice)][index - 1] += 1

#     return {
#         "message": "success",
#         "englishCount": englishCount,
#         }

# @router.post("/getFilteredDataScience/")
# async def get_filtered_data(request: Request):

#     data = await request.json()
#     start_date = data.get("start")
#     end_date = data.get("end")

#     query = {
#     "date": {"$gte": start_date, "$lte": end_date}
#     }

#     question_count = 30

#     itemCount = {
#     "0": [0] * question_count,
#     "1": [0] * question_count,
#     "2": [0] * question_count,
#     "3": [0] * question_count,
#     "4": [0] * question_count
#     }

#     result = list(collection3.find(query))
    
#     for batch in result:
#         for applicants in batch["applicants"]: #applicants
#             for index, choice in enumerate(applicants["applicantKeyScience"], start=1):
#                 if isinstance(choice, int):
#                     if choice != -1:
#                         itemCount[str(choice)][index - 1] += 1

#     return {
#         "message": "success",
#         "scienceCount": itemCount,
#         }

# @router.get("/getAnalysisDataScience/")
# async def get_analysis_data():
#     question_count = 30

# # Initialize dictionaries to count choices
#     scienceCount = {
#     "0": [0] * question_count,
#     "1": [0] * question_count,
#     "2": [0] * question_count,
#     "3": [0] * question_count,
#     "4": [0] * question_count
# }
#     data = list(collection3.find())
    
#     for batch in data:
#         for applicants in batch["applicants"]: #applicants
#             for index, choice in enumerate(applicants["applicantKeyScience"], start=1):
#                 if isinstance(choice, int):
#                     if choice != -1:
#                         scienceCount[str(choice)][index - 1] += 1
#     return {
#         "message": "success",
#         "scienceCount": scienceCount,
#         }

# @router.post("/getFilteredDataMath/")
# async def get_filtered_data(request: Request):

#     data = await request.json()
#     start_date = data.get("start")
#     end_date = data.get("end")

#     query = {
#     "date": {"$gte": start_date, "$lte": end_date}
#     }

#     question_count = 30

#     itemCount = {
#     "0": [0] * question_count,
#     "1": [0] * question_count,
#     "2": [0] * question_count,
#     "3": [0] * question_count,
#     "4": [0] * question_count
#     }

#     result = list(collection3.find(query))
    
#     for batch in result:
#         for applicants in batch["applicants"]: #applicants
#             for index, choice in enumerate(applicants["applicantKeyMathematics"], start=1):
#                 if isinstance(choice, int):
#                     if choice != -1:
#                         itemCount[str(choice)][index - 1] += 1

#     return {
#         "message": "success",
#         "mathCount": itemCount,
#         }

# @router.get("/getAnalysisDataMath/")
# async def get_analysis_data():
#     question_count = 30

# # Initialize dictionaries to count choices

#     mathCount = {
#     "0": [0] * question_count,
#     "1": [0] * question_count,
#     "2": [0] * question_count,
#     "3": [0] * question_count,
#     "4": [0] * question_count
# }

#     data = list(collection3.find())
    
#     for batch in data:
#         for applicants in batch["applicants"]: #applicants
#             for index, choice in enumerate(applicants["applicantKeyMathematics"], start=1):
#                 if isinstance(choice, int):
#                     if choice != -1:
#                         mathCount[str(choice)][index - 1] += 1

#     return {
#         "message": "success",
#         "mathCount": mathCount,
#         }

# @router.post("/getFilteredDataAptitude/")
# async def get_filtered_data(request: Request):

#     data = await request.json()
#     start_date = data.get("start")
#     end_date = data.get("end")

#     query = {
#     "date": {"$gte": start_date, "$lte": end_date}
#     }

#     question_count = 30

#     itemCount = {
#     "0": [0] * question_count,
#     "1": [0] * question_count,
#     "2": [0] * question_count,
#     "3": [0] * question_count,
#     "4": [0] * question_count
#     }

#     result = list(collection3.find(query))
    
#     for batch in result:
#         for applicants in batch["applicants"]: #applicants
#             for index, choice in enumerate(applicants["applicantKeyAptitude"], start=1):
#                 if isinstance(choice, int):
#                     if choice != -1:
#                         itemCount[str(choice)][index - 1] += 1

#     return {
#         "message": "success",
#         "aptitudeCount": itemCount,
#         }

# @router.get("/getAnalysisDataAptitude/")
# async def get_analysis_data():
#     question_count = 30

# # Initialize dictionaries to count choices

#     aptitudeCount = {
#     "0": [0] * question_count,
#     "1": [0] * question_count,
#     "2": [0] * question_count,
#     "3": [0] * question_count,
#     "4": [0] * question_count
# }
#     data = list(collection3.find())
    
#     for batch in data:
#         for applicants in batch["applicants"]: #applicants
#             for index, choice in enumerate(applicants["applicantKeyAptitude"], start=1):
#                 if isinstance(choice, int):
#                     if choice != -1:
#                         aptitudeCount[str(choice)][index - 1] += 1

#     return {
#         "message": "success",
#         "aptitudeCount": aptitudeCount,
#         }