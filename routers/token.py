from fastapi import APIRouter, Depends, Request, Response, Cookie
from db.async_db import get_db
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
import models
from services.auth import (create_access_token, create_refresh_token,
                           verify_refresh_token, set_user_authorized_state)



logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/token',
    tags=['Token']
)


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    refresh_token: Optional[str] = Cookie(None)
):
    if not refresh_token:
        return JSONResponse(status_code=401, content={"error": "No refresh token provided"})

    try:
        user_id = verify_refresh_token(refresh_token)
    except Exception as e:
        return JSONResponse(status_code=401, content={"error": "Invalid refresh token"})

    if not user_id:
        return JSONResponse(status_code=401, content={"error": "Invalid refresh token"})

    user = await db.get(models.User, user_id)
    if not user:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    try:
        new_access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token(user.id)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to create new tokens"})

    response.set_cookie(key="access_token", value=new_access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True)

    try:
        await set_user_authorized_state(request, user)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to set user authorized state"})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "status_code": 200}


@router.get('/set')
async def setting(response: Response):
    response.set_cookie(key='refresh_token', value=create_refresh_token(), httponly=True)
    return {'message': 'Refresh token set'}