from fastapi import HTTPException, status, Depends
from sqlalchemy.orm.exc import NoResultFound
from models import Roles
from services.auth import get_current_user

