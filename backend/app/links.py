import secrets
import string
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Link
from app.schemas import LinkCreate, LinkOut

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 7
MAX_ATTEMPTS = 5

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


def generate_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


@router.post("/api/links", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
def create_link(payload: LinkCreate, session: SessionDep) -> Link:
    # 62^7 possible codes make collisions rare; the unique index catches the rest.
    for _ in range(MAX_ATTEMPTS):
        link = Link(code=generate_code(), target_url=str(payload.target_url))
        session.add(link)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            continue
        session.refresh(link)
        return link
    raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Could not generate a unique code")


@router.get("/api/links", response_model=list[LinkOut])
def list_links(session: SessionDep, limit: int = 50) -> list[Link]:
    limit = max(1, min(limit, 100))
    stmt = select(Link).order_by(Link.created_at.desc(), Link.id.desc()).limit(limit)
    return list(session.scalars(stmt))


@router.get("/r/{code}")
def follow_link(code: str, session: SessionDep) -> RedirectResponse:
    # Single atomic UPDATE: safe when many backend replicas count clicks at once.
    stmt = (
        update(Link)
        .where(Link.code == code)
        .values(clicks=Link.clicks + 1)
        .returning(Link.target_url)
    )
    target_url = session.scalar(stmt)
    if target_url is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Link not found")
    session.commit()
    return RedirectResponse(target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
