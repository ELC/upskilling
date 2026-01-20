"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from upskills.core.security import verify_token
from upskills.db.provider import DatabaseProvider
from upskills.models.db.user import User
from upskills.repositories.user import UserRepository

# Security scheme
security = HTTPBearer()


async def get_db_provider(request: Request) -> DatabaseProvider:
    """Get the database provider from the app state."""
    return request.app.state.container.db_provider()


async def get_db_session(
    db_provider: Annotated[DatabaseProvider, Depends(get_db_provider)],
) -> AsyncSession:
    """Get a database session."""
    return await db_provider.get_session()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    """Get the current authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    user_id_str = verify_token(token, "access")

    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User | None:
    """Get the current user if authenticated, otherwise None."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    user_id_str = verify_token(token, "access")

    if user_id_str is None:
        return None

    try:
        user_id = int(user_id_str)
    except ValueError:
        return None

    repo = UserRepository(session)
    return await repo.get_by_id(user_id)


def require_permissions(*required_permissions: str):
    """Dependency factory that checks if user has required permissions."""

    async def check_permissions(
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> User:
        repo = UserRepository(session)
        user_permissions = await repo.get_user_permissions(current_user.user_id)

        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {permission}",
                )

        return current_user

    return check_permissions


# Type aliases for common dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
