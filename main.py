from routers import posts, auth, users, admin, topic, subscription, token, notification
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


OAuth2_SCHEME = OAuth2PasswordBearer('auth/login/')

app = FastAPI()


app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(topic.router)
app.include_router(subscription.router)
app.include_router(token.router)
app.include_router(notification.router)


@app.get('/')
async def index():
    return {'messege': 'Hello World'}

