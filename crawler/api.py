from fastapi import FastAPI
from scheduler_my import app as app_rocketry

app = FastAPI()
session = app_rocketry.session


@app.get("/check-workin")
async def check_workin():
    print('P3')
    return True


@app.get("/tasks")
async def get_tasks():
    return session.tasks


@app.post("/my-route")
async def manipulate_session():
    for task in session.tasks:
        print('P2')
        pass
    return True