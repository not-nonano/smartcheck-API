from fastapi import FastAPI

from routers import users, answer_key, omr, school_data, test 

from models import answer_key

app = FastAPI()

app.include_router(users.router)
app.include_router(answer_key.router)
app.include_router(omr.router)
app.include_router(school_data.router)
app.include_router(test.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    