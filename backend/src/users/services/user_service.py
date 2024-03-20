from typing import Optional

from django.contrib.auth.hashers import check_password

from src.common.responses import ORJSONResponse
from src.users.errors import (
    EmailAlreadyExists,
    NotAuthenticated,
    UsernameAlreadyExists,
    UserNotFound,
)
from src.users.schemas import (
    SuperUserCreateErrorSchema,
    SuperUserCreateSchema,
    SuperUserCreateSuccessSchema,
)
from src.users.types import UserType


class UserService:
    def __init__(self, repository, *args, **kwargs):
        self.user_repository = repository
        super().__init__(*args, **kwargs)

    def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> Optional["UserType"]:
        user = self.user_repository.get_user_by_username(username)
        if user is None:
            raise UserNotFound
        if not check_password(password, user.password):
            raise NotAuthenticated
        return user

    def create_superuser(
        self,
        user_super_create: "SuperUserCreateSchema",
    ) -> Optional["ORJSONResponse"]:
        if self.user_repository.get_user_by_email(
            email=user_super_create.email,
        ):
            raise EmailAlreadyExists

        if self.user_repository.get_user_by_username(
            username=user_super_create.username,
        ):
            raise UsernameAlreadyExists

        if self.user_repository.create_superuser(
            user_super_create=user_super_create,
        ):
            return ORJSONResponse(
                data=SuperUserCreateSuccessSchema(
                    message="User created successfully"
                ).model_dump(),
                status=201,
            )

        return ORJSONResponse(
            data=SuperUserCreateErrorSchema(
                message="Error while creating superuser"
            ).model_dump(),
            status=400,
        )
