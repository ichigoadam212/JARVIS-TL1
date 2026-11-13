"""Small authorization policy for commands.

Principal objects must be created by a trusted authentication layer. This
module does not authenticate users or establish owner identity by itself.
"""
from dataclasses import dataclass
from enum import Enum


class AccessLevel(str, Enum):
    PUBLIC = "public"
    OWNER_ONLY = "owner_only"
    SECRET_OWNER_ONLY = "secret_owner_only"


@dataclass(frozen=True, slots=True)
class Principal:
    subject: str = "anonymous"
    is_owner: bool = False
    secret_mode_authorized: bool = False


class CommandPolicy:
    """Default-deny authorization for privileged command registrations."""

    @staticmethod
    def allows(access_level: AccessLevel, principal: Principal) -> bool:
        if access_level is AccessLevel.PUBLIC:
            return True
        if access_level is AccessLevel.OWNER_ONLY:
            return principal.is_owner and principal.subject != "anonymous"
        if access_level is AccessLevel.SECRET_OWNER_ONLY:
            return (
                principal.is_owner
                and principal.subject != "anonymous"
                and principal.secret_mode_authorized
            )
        return False
