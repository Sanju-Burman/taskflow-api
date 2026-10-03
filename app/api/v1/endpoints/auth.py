from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.base import DataResponse
from app.schemas.user import Token, UserCreate, UserLogin, UserRead, UserWithToken
from app.services.user_service import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=DataResponse[UserWithToken],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    db: SessionDep,
    user_in: UserCreate,
) -> DataResponse[UserWithToken]:
    """Register a new user account with email and password."""
    result = await user_service.register(db, user_in=user_in)
    return DataResponse(
        success=True,
        message="User registered successfully.",
        data=result,
    )


@router.post(
    "/login",
    response_model=DataResponse[UserWithToken],
    status_code=status.HTTP_200_OK,
    summary="Authenticate with email and password",
)
async def login(
    db: SessionDep,
    login_data: UserLogin,
) -> DataResponse[UserWithToken]:
    """Authenticate with standard JSON payload and receive JWT tokens."""
    result = await user_service.authenticate(db, login_data=login_data)
    return DataResponse(
        success=True,
        message="Login successful.",
        data=result,
    )


@router.post(
    "/login/oauth",
    response_model=Token,
    summary="OAuth2 compatible token login for Swagger UI",
)
async def login_oauth(
    db: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """OAuth2 password form login endpoint for Swagger UI Authorize button integration."""
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    result = await user_service.authenticate(db, login_data=login_data)
    return result.token


@router.get(
    "/me",
    response_model=DataResponse[UserRead],
    summary="Retrieve current user profile",
)
async def get_current_user_profile(
    current_user: CurrentUserDep,
) -> DataResponse[UserRead]:
    """Get the authenticated user's profile details."""
    return DataResponse(
        success=True,
        data=UserRead.model_validate(current_user),
    )
