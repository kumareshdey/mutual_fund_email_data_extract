from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from service import get_user_data
import uvicorn

app = FastAPI()

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials):
    correct_username = "admin"
    correct_password = "password"
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/user_data")
def user_data(pan_no: str = None, credentials: HTTPBasicCredentials = Depends(security)):
    authenticate(credentials)
    return get_user_data(pan_no=pan_no)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

