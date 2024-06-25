import posts
import users
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer


OAuth2_SCHEME = OAuth2PasswordBearer('user/login/')

app = FastAPI()


app.include_router(posts.router)
app.include_router(users.router)

@app.get('/')
async def index():
    return {'messege': 'Hello World'}