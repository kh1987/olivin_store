import logging
from typing import Any, Optional

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from ninja.security import HttpBearer

from src.auth.errors import InvalidToken, UserNotFound
from src.auth.utils import decode_jwt_token
from src.common.utils import pydantic_model
from src.users.repositories import UserRepository

logger = logging.getLogger(__name__)


def get_user_id(request: HttpRequest) -> Optional[dict]:
    user_id = request.user.id if request.user else None
    payload = get_token_payload(request=request)

    if payload:
        user_id = payload.get("user_id")

    return pydantic_model(user_id=user_id) if user_id else None


def get_token_payload(request: HttpRequest) -> Optional[dict]:
    header = "Authorization"
    headers = request.headers
    auth_value = headers.get(header)
    if not auth_value:
        return None
    parts = auth_value.split(" ")
    token = " ".join(parts[1:])
    try:
        decode_token = decode_jwt_token(token)
        if decode_token:
            return decode_token
    except Exception as error:
        logger.exception(error)
        raise InvalidToken


class AuthBearer(HttpBearer):
    user_model = get_user_model()
    repository = UserRepository()

    def get_user(self, request: HttpRequest, user_id: Any) -> None:
        try:
            user = self.repository.get_user_by_id(user_id=user_id)
            request.user = user
        except Exception as error:
            logger.exception(error)
            raise UserNotFound

    def authenticate(self, request: HttpRequest, token: str) -> Optional[dict]:
        try:
            decode_token = decode_jwt_token(token)
            if decode_token:
                self.get_user(request=request, user_id=decode_token.get("user_id"))
                return decode_token
        except Exception as error:
            logger.exception(error)
            raise InvalidToken
