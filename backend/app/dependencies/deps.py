from fastapi import Depends, Header, HTTPException
from ..core.security import decode_token


def get_token(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing auth")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth")
    token = authorization.split(" ", 1)[1]
    td = decode_token(token)
    if td is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return td.sub
