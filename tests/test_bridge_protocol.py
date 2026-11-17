from dataclasses import replace

import pytest

from jarvis.bridge.protocol import (
    BridgeAction,
    BridgeAuthenticationError,
    BridgeAuthenticator,
    BridgeProtocolError,
    BridgeRequest,
)


SECRET = "bridge-test-secret-that-is-at-least-32-bytes-long"
NOW = 1_800_000_000


def make_authenticator(**kwargs):
    return BridgeAuthenticator(SECRET, clock=lambda: NOW, **kwargs)


@pytest.mark.parametrize(
    "action",
    [BridgeAction.STATUS_READ, BridgeAction.CAPABILITIES_READ],
)
def test_read_only_request_is_signed_and_verified(action):
    sender = make_authenticator()
    receiver = make_authenticator()

    request = sender.create_request(action)

    assert request.protocol_version == 1
    assert request.payload == {}
    assert len(request.signature) == 64
    assert receiver.verify(request) is None


def test_request_tampering_invalidates_signature():
    sender = make_authenticator()
    receiver = make_authenticator()
    request = sender.create_request(BridgeAction.STATUS_READ)

    tampered = replace(request, timestamp=request.timestamp + 1)

    with pytest.raises(BridgeAuthenticationError, match="signature"):
        receiver.verify(tampered)


def test_replayed_nonce_is_rejected():
    sender = make_authenticator()
    receiver = make_authenticator()
    request = sender.create_request(BridgeAction.STATUS_READ)

    receiver.verify(request)
    with pytest.raises(BridgeAuthenticationError, match="already been used"):
        receiver.verify(request)


def test_stale_request_is_rejected():
    sender = make_authenticator()
    receiver = make_authenticator()
    request = sender.create_request(BridgeAction.STATUS_READ, timestamp=NOW - 60)

    with pytest.raises(BridgeAuthenticationError, match="time window"):
        receiver.verify(request)


def test_future_request_outside_clock_window_is_rejected():
    sender = make_authenticator()
    receiver = make_authenticator()
    request = sender.create_request(BridgeAction.STATUS_READ, timestamp=NOW + 60)

    with pytest.raises(BridgeAuthenticationError, match="time window"):
        receiver.verify(request)


def test_read_only_protocol_rejects_payloads():
    authenticator = make_authenticator()

    with pytest.raises(BridgeProtocolError, match="do not accept payload"):
        authenticator.create_request(BridgeAction.STATUS_READ, payload={"command": "status"})


def test_unknown_or_privileged_action_is_rejected():
    authenticator = make_authenticator()

    with pytest.raises(BridgeProtocolError, match="Unsupported bridge action"):
        authenticator.create_request("process.restart")


def test_protocol_version_is_checked_before_authentication():
    authenticator = make_authenticator()
    request = authenticator.create_request(BridgeAction.STATUS_READ)
    invalid = replace(request, protocol_version=2)

    with pytest.raises(BridgeProtocolError, match="version"):
        authenticator.verify(invalid)


def test_nonce_cache_fails_closed_when_capacity_is_full():
    sender = make_authenticator()
    receiver = make_authenticator(max_nonces=1)
    first = sender.create_request(BridgeAction.STATUS_READ)
    second = sender.create_request(BridgeAction.CAPABILITIES_READ)

    receiver.verify(first)
    with pytest.raises(BridgeAuthenticationError, match="capacity is full"):
        receiver.verify(second)


@pytest.mark.parametrize("secret", ["short", b"short", None])
def test_short_or_invalid_secret_is_rejected(secret):
    with pytest.raises(ValueError, match="at least 32 bytes"):
        BridgeAuthenticator(secret)


def test_malformed_request_id_and_nonce_are_rejected():
    authenticator = make_authenticator()
    request = authenticator.create_request(BridgeAction.STATUS_READ)

    with pytest.raises(BridgeProtocolError, match="request ID"):
        authenticator.verify(replace(request, request_id="bad"))

    with pytest.raises(BridgeProtocolError, match="nonce"):
        authenticator.verify(replace(request, nonce="bad"))
