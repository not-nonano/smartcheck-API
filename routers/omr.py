import platform
from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import csv, shutil, os, glob, subprocess, time

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

async def read_csv_file(file_path):
    data = {}

    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        variables = next(reader)  # Read the first row as variable names
        values = next(reader)  # Read the second row as values

        # Populate the data dictionary
        for variable, value in zip(variables, values):
            if variable in ['file_id', 'input_path', 'output_path']:
                data[variable] = value
            else:
                prefix = variable.split('q')[0]
                var_name = variable.split('q')[1] if len(
                    variable.split('q')) > 1 else ''

                if prefix not in data:
                    data[prefix] = {}

                data[prefix][var_name] = value

    return data


async def delete_files(filename):
    # Specify the folder path where the CSV files are located
    csv_path = f'./OMRChecker/outputs/{filename}'
    input_path = f'./OMRChecker/inputs/{filename}'

    shutil.rmtree(csv_path)
    shutil.rmtree(input_path)



@router.post('/upload')
async def upload_file(request: Request):
    form = await request.form()
    file = form['file'].file
    filename = form['file'].filename
    batchId = form['batchId']
    id = int(form['id'])

    # Specify the folder where you want to save the image
    upload_folder = f'./OMRChecker/inputs/{filename}'

    # Create the folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    # Save the file to the upload folder
    file_path = os.path.join(upload_folder, filename)
    with open(file_path, 'wb') as f:
        f.write(file.read())

    shutil.copy2("OMRChecker/inputs/template.json", f"OMRChecker/inputs/{filename}/")

    command = ["python", "OMRChecker/main.py", "--inputDir",
               f"OMRChecker/inputs/{filename}", "--outputDir", f"OMRChecker/outputs/{filename}"]
    
    operating_system = platform.system()

    if operating_system == "Linux":
        command = ["x-terminal-emulator", "-e", "python", "OMRChecker/main.py", "--inputDir", f"OMRChecker/inputs/{filename}", "--outputDir", f"OMRChecker/outputs/{filename}"]
        subprocess.Popen(command).wait()
    elif operating_system == "Windows":
        command = ["cmd", "/c", "python", "OMRChecker/main.py", "--inputDir", f"OMRChecker/inputs/{filename}", "--outputDir", f"OMRChecker/outputs/{filename}"]
        subprocess.Popen(command).wait()

    answerKey = collection2.find_one(sort=[("date", -1)])

    current_directory = f'./OMRChecker/outputs/{filename}/Results'
    csv_pattern = "*.csv"
    csv_files = glob.glob(os.path.join(current_directory, csv_pattern))

    try:
        if csv_files:
            for csv_file in csv_files:
                data = await read_csv_file(csv_file)
                ans_english = data['eng']
                ans_math = data['math']
                ans_science = data['sci']
                ans_aptitude = data['apt']

                key1 = answerKey['english']
                key2 = answerKey['mathematics']
                key3 = answerKey['science']
                key4 = answerKey['aptitude']

                applicantScoreEnglish = 0
                applicantScoreMathematics = 0
                applicantScoreScience = 0
                applicantScoreAptitude = 0

                applicantKeyEnglish = []
                applicantKeyMathematics = []
                applicantKeyScience = []
                applicantKeyAptitude = []

                for i in range(1, 31):
                    try:
                        if ans_english[str(i)] == key1[i - 1]:
                            applicantScoreEnglish += 1
                        if ans_math[str(i)] == key2[i - 1]:
                            applicantScoreMathematics += 1
                        if ans_science[str(i)] == key3[i - 1]:
                            applicantScoreScience += 1
                        if i <= 15 and ans_aptitude[str(i)] == key4[i - 1]:
                            applicantScoreAptitude += 1

                        applicantKeyEnglish.append(
                            0 if ans_english[str(i)] == 'A' else
                            1 if ans_english[str(i)] == 'B' else
                            2 if ans_english[str(i)] == 'C' else
                            3 if ans_english[str(i)] == 'D' else
                            4 if ans_english[str(i)] == 'E' else
                            -1
                        )
                        applicantKeyMathematics.append(
                            0 if ans_math[str(i)] == 'A' else
                            1 if ans_math[str(i)] == 'B' else
                            2 if ans_math[str(i)] == 'C' else
                            3 if ans_math[str(i)] == 'D' else
                            -1
                        )
                        applicantKeyScience.append(
                            0 if ans_science[str(i)] == 'A' else
                            1 if ans_science[str(i)] == 'B' else
                            2 if ans_science[str(i)] == 'C' else
                            3 if ans_science[str(i)] == 'D' else
                            -1
                        )
                        if i <= 15:
                            applicantKeyAptitude.append(
                            0 if ans_aptitude[str(i)] == 'A' else
                            1 if ans_aptitude[str(i)] == 'B' else
                            2 if ans_aptitude[str(i)] == 'C' else
                            3 if ans_aptitude[str(i)] == 'D' else
                            -1
                        )
                    except Exception as e:
                        return JSONResponse({'message': f'Error processing CSV: {e}', 'status': "fail"})
                
                count = 0
                for element in applicantKeyEnglish:
                    if element == -1:
                        count += 1
                for element in applicantKeyScience:
                    if element == -1:
                        count += 1
                for element in applicantKeyMathematics:
                    if element == -1:
                        count += 1
                for element in applicantKeyAptitude:
                    if element == -1:
                        count += 1

                # if count > 10:
                #     return JSONResponse({'message': 'Retake the photo', 'status': "fail"})

                collection3 = db["applicantlist"]
                data = collection3.find_one({'_id': batchId})

                total_score = applicantScoreEnglish + applicantScoreMathematics + applicantScoreScience + applicantScoreAptitude
                average = total_score / 4
                result = ""

                if average >= 85:
                    result = "Above Average"
                elif average >= 60:
                    result = "Average"
                elif average >= 40:
                    result = "Below Average"
                else:
                    result = "Poor"

                data["applicants"][id]["applicantKeyEnglish"] = applicantKeyEnglish
                data["applicants"][id]["applicantKeyMathematics"] = applicantKeyMathematics
                data["applicants"][id]["applicantKeyScience"] = applicantKeyScience
                data["applicants"][id]["applicantKeyAptitude"] = applicantKeyAptitude
                data["applicants"][id]["English"] = applicantScoreEnglish
                data["applicants"][id]["Mathematics"] = applicantScoreMathematics
                data["applicants"][id]["Science"] = applicantScoreScience
                data["applicants"][id]["Aptitude"] = applicantScoreAptitude
                data["applicants"][id]["Result"] = result
                data["applicants"][id]["status"] = True

                filter = {'_id': batchId}
                newvalues = {"$set": {"applicants": data["applicants"]}}

                result = collection3.update_one(filter, newvalues)
            #await delete_files(filename)

        else:
            await delete_files(filename)
            return JSONResponse({'message': 'Please try again. ', 'status': 'success'})
    except Exception as e:
        return JSONResponse({'message': f'Error: {e}', 'status': 'fail'})

    return JSONResponse({'message': 'File uploaded successfully', 'status': 'success'})