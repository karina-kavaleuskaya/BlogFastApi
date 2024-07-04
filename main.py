from routers import posts, auth, users, admin, topic, subscription
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer


OAuth2_SCHEME = OAuth2PasswordBearer('auth/login/')

app = FastAPI()


app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(topic.router)
app.include_router(subscription.router)


@app.get('/')
async def index():
    return {'messege': 'Hello World'}