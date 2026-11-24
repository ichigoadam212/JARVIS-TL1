"""Authenticated, read-only message envelope for the future Android Bridge.

This module defines protocol primitives only. It opens no sockets, executes no
commands, and does not authenticate an owner or authorize privileged actions.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import json
import re
import secrets
from threading import Lock
from time import time
from typing import Any


PROTOCOL_VERSION = 1
MAX_ENVELOPE_BYTES = 4096
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
_NONCE_RE = re.compile(r"^[A-Za-z0-9_-]{22,128}$")
_SIGNATURE_RE = re.compile(r"^[0-9a-f]{64}$")


class BridgeAction(str, Enum):
    """Only read-only discovery actions are supported in protocol v1."""

    STATUS_READ = "status.read"
    CAPABILITIES_READ = "capabilities.read"


class BridgeProtocolError(ValueError):
    """The request is malformed or uses an unsupported protocol feature."""


class BridgeAuthenticationError(BridgeProtocolError):
    """The request failed authentication, freshness, or replay checks."""


@dataclass(frozen=True, slots=True)
class BridgeRequest:
    """A signed bridge request; payloads are empty until a schema is defined."""

    protocol_version: int
    request_id: str
    action: BridgeAction
    timestamp: int
    nonce: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    signature: str = ""


def _canonical_bytes(request: BridgeRequest) -> bytes:
    if type(request.protocol_version) is not int or request.protocol_version != PROTOCOL_VERSION:
        raise BridgeProtocolError("Unsupported bridge protocol version.")
    if not isinstance(request.request_id, str) or not _REQUEST_ID_RE.fullmatch(request.request_id):
        raise BridgeProtocolError("Invalid bridge request ID.")
    if not isinstance(request.action, BridgeAction):
        raise BridgeProtocolError("Unsupported bridge action.")
    if type(request.timestamp) is not int or request.timestamp < 0:
        raise BridgeProtocolError("Invalid bridge timestamp.")
    if not isinstance(request.nonce, str) or not _NONCE_RE.fullmatch(request.nonce):
        raise BridgeProtocolError("Invalid bridge nonce.")
    if not isinstance(request.payload, Mapping):
        raise BridgeProtocolError("Bridge payload must be an object.")
    if request.payload:
        raise BridgeProtocolError("Protocol v1 read-only actions do not accept payload data.")

    envelope = {
        "protocol_version": request.protocol_version,
        "request_id": request.request_id,
        "action": request.action.value,
        "timestamp": request.timestamp,
        "nonce": request.nonce,
        "payload": {},
    }
    try:
        encoded = json.dumps(
            envelope,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise BridgeProtocolError("Bridge request is not valid JSON.") from error
    if len(encoded) > MAX_ENVELOPE_BYTES:
        raise BridgeProtocolError("Bridge request exceeds the envelope size limit.")
    return encoded


@dataclass(slots=True)
class _ReplayState:
    """Replay state shared by every authenticator using the same secret."""

    max_clock_skew_seconds: int
    max_nonces: int
    seen_nonces: dict[str, int] = field(default_factory=dict)
    highest_wall_time_seen: int | None = None
    lock: Lock = field(default_factory=Lock, repr=False)


class BridgeAuthenticator:
    """HMAC authentication plus bounded, process-local nonce replay protection.

    Replay state is shared across authenticator instances that use the same
    secret. Verification also tracks a nondecreasing wall-clock high-water
    mark; backward clock movement fails closed until the clock catches up.

    The secret must be provisioned outside the repository and supplied in
    memory. The same secret must be provisioned securely to both peers.
    """

    _replay_states: dict[bytes, _ReplayState] = {}
    _replay_states_lock = Lock()

    def __init__(
        self,
        secret: bytes | str,
        *,
        max_clock_skew_seconds: int = 30,
        max_nonces: int = 4096,
        clock: Callable[[], float] = time,
    ) -> None:
        key = secret.encode("utf-8") if isinstance(secret, str) else secret
        if not isinstance(key, bytes) or len(key) < 32:
            raise ValueError("Bridge secret must contain at least 32 bytes.")
        if type(max_clock_skew_seconds) is not int or max_clock_skew_seconds < 1:
            raise ValueError("max_clock_skew_seconds must be a positive integer.")
        if type(max_nonces) is not int or max_nonces < 1:
            raise ValueError("max_nonces must be a positive integer.")

        key_id = hashlib.sha256(key).digest()
        with self._replay_states_lock:
            replay_state = self._replay_states.get(key_id)
            if replay_state is None:
                replay_state = _ReplayState(max_clock_skew_seconds, max_nonces)
                self._replay_states[key_id] = replay_state
            elif (
                replay_state.max_clock_skew_seconds != max_clock_skew_seconds
                or replay_state.max_nonces != max_nonces
            ):
                raise ValueError(
                    "Bridge authenticators using the same secret must use the same replay limits."
                )

        self._secret = key
        self._max_clock_skew = max_clock_skew_seconds
        self._max_nonces = max_nonces
        self._clock = clock
        self._replay_state = replay_state

    def create_request(
        self,
        action: BridgeAction,
        *,
        request_id: str | None = None,
        nonce: str | None = None,
        timestamp: int | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> BridgeRequest:
        """Create a signed request for one of the protocol's read-only actions."""
        request = BridgeRequest(
            protocol_version=PROTOCOL_VERSION,
            request_id=request_id or secrets.token_urlsafe(12),
            action=action,
            timestamp=int(self._clock()) if timestamp is None else timestamp,
            nonce=nonce or secrets.token_urlsafe(24),
            payload={} if payload is None else payload,
        )
        signature = hmac.new(self._secret, _canonical_bytes(request), hashlib.sha256).hexdigest()
        return BridgeRequest(
            protocol_version=request.protocol_version,
            request_id=request.request_id,
            action=request.action,
            timestamp=request.timestamp,
            nonce=request.nonce,
            payload={},
            signature=signature,
        )

    def verify(self, request: BridgeRequest) -> None:
        """Verify authenticity and freshness, then consume the nonce once."""
        if not isinstance(request, BridgeRequest):
            raise BridgeProtocolError("Expected a BridgeRequest envelope.")
        signed_content = _canonical_bytes(request)
        if not isinstance(request.signature, str) or not _SIGNATURE_RE.fullmatch(request.signature):
            raise BridgeAuthenticationError("Invalid bridge signature format.")

        expected = hmac.new(self._secret, signed_content, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, request.signature):
            raise BridgeAuthenticationError("Bridge signature verification failed.")

        now = int(self._clock())
        replay_state = self._replay_state
        with replay_state.lock:
            if replay_state.highest_wall_time_seen is not None and now < replay_state.highest_wall_time_seen:
                raise BridgeAuthenticationError(
                    "Bridge system clock moved backwards; replay checks are paused until it catches up."
                )
            replay_state.highest_wall_time_seen = now

            if abs(now - request.timestamp) > self._max_clock_skew:
                raise BridgeAuthenticationError("Bridge request is outside the allowed time window.")

            expires_at = request.timestamp + self._max_clock_skew
            expired = [value for value, expiry in replay_state.seen_nonces.items() if expiry < now]
            for value in expired:
                replay_state.seen_nonces.pop(value, None)

            if request.nonce in replay_state.seen_nonces:
                raise BridgeAuthenticationError("Bridge request nonce has already been used.")
            if len(replay_state.seen_nonces) >= self._max_nonces:
                raise BridgeAuthenticationError("Bridge replay-protection capacity is full.")

            replay_state.seen_nonces[request.nonce] = expires_at
