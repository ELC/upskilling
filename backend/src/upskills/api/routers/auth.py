"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from upskills.core.dependencies import DbSession, CurrentUser
from upskills.models.domain.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from upskills.models.domain.user import (
    PasswordReset,
    PasswordResetRequest,
    UserResponse,
)
from upskills.models.domain.base import MessageResponse
from upskills.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    session: DbSession,
) -> AuthResponse:
    """Register a new user account."""
    service = AuthService(session)

    try:
        result = await service.register(
            full_name=data.full_name,
            email=data.email,
            password=data.password,
            bio=data.bio,
        )
        await session.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    session: DbSession,
) -> AuthResponse:
    """Authenticate and get access tokens."""
    service = AuthService(session)

    try:
        return await service.login(data.email, data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: RefreshTokenRequest,
    session: DbSession,
) -> TokenResponse:
    """Refresh access and refresh tokens."""
    service = AuthService(session)

    try:
        return await service.refresh_tokens(data.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/password-reset-request", response_model=MessageResponse)
async def request_password_reset(
    data: PasswordResetRequest,
    session: DbSession,
) -> MessageResponse:
    """Request a password reset email."""
    service = AuthService(session)

    token = await service.request_password_reset(data.email)
    await session.commit()

    # In production, send email with token
    # For now, return success regardless (don't reveal if email exists)
    if token:
        # Log or send email with token
        # In a real app: send_password_reset_email(data.email, token)
        pass

    return MessageResponse(
        message="If the email exists, a password reset link has been sent.",
    )


@router.post("/password-reset", response_model=MessageResponse)
async def reset_password(
    data: PasswordReset,
    session: DbSession,
) -> MessageResponse:
    """Reset password using a reset token."""
    service = AuthService(session)

    try:
        success = await service.reset_password(data.token, data.new_password)
        await session.commit()

        if success:
            return MessageResponse(message="Password has been reset successfully.")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password.",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
) -> UserResponse:
    """Get the current authenticated user's information."""
    from upskills.models.domain.user import RoleResponse

    roles = []
    if current_user.roles:
        for user_role in current_user.roles:
            if user_role.role:
                roles.append(RoleResponse(
                    role_id=user_role.role.role_id,
                    name=user_role.role.name,
                    description=user_role.role.description,
                    max_active_paths=user_role.role.max_active_paths,
                ))

    return UserResponse(
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        bio=current_user.bio,
        created_at=current_user.created_at,
        roles=roles,
    )
