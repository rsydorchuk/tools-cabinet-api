import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from jwt import PyJWTError

from ..services.auth_service import COOKIE_NAME, decode_access_token


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")
    try:
        return decode_access_token(token)
    except PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")


async def get_current_user_id(current_user: Annotated[dict, Depends(get_current_user)]) -> uuid.UUID:
    return uuid.UUID(current_user["sub"])
