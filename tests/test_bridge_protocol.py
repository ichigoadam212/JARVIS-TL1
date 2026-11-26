from dataclasses import replace

import pytest

from jarvis.bridge.protocol import (
    MAX_NONCES_PER_KEY,
    MAX_REPLAY_STATES,
    BridgeAction,
    BridgeAuthenticationError,
    BridgeAuthenticator,
    BridgeProtocolError,
    BridgeRequest,
)


SECRET = "bridge-test-secret-that-is-at-least-32-bytes-long"
NOW = 1_800_000_000


@pytest.fixture(autouse=True)
def reset_process_replay_state():
    with BridgeAuthenticator._replay_states_lock:
        BridgeAuthenticator._replay_states.clear()


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


def test_replay_state_is_shared_across_instances_with_the_same_secret():
    sender = make_authenticator()
    first_receiver = make_authenticator()
    second_receiver = make_authenticator()
    request = sender.create_request(BridgeAction.STATUS_READ)

    first_receiver.verify(request)
    with pytest.raises(BridgeAuthenticationError, match="already been used"):
        second_receiver.verify(request)


def test_authenticators_with_same_secret_require_matching_replay_limits():
    make_authenticator(max_clock_skew_seconds=30, max_nonces=64)

    with pytest.raises(ValueError, match="same replay limits"):
        make_authenticator(max_clock_skew_seconds=60, max_nonces=64)


def test_stale_request_is_rejected():
    sender = make_authenticator()
    receiver = make_authenticator()
    request = sender.create_request(BridgeAction.STATUS_READ, timestamp=NOW - 60)

    with pytest.raises(BridgeAuthenticationError, match="time window"):
        receiver.verify(request)


def test_clock_rollback_cannot_reenable_an_expired_nonce_across_instances():
    clock_value = [NOW]
    clock = lambda: clock_value[0]
    sender = BridgeAuthenticator(SECRET, clock=clock)
    first_receiver = BridgeAuthenticator(SECRET, clock=clock)
    second_receiver = BridgeAuthenticator(SECRET, clock=clock)

    first = sender.create_request(BridgeAction.STATUS_READ)
    first_receiver.verify(first)

    # Advancing beyond the first request's expiry removes its nonce from the
    # bounded cache. A separate authenticator must still reject it after rollback.
    clock_value[0] = NOW + 31
    forward = sender.create_request(BridgeAction.CAPABILITIES_READ)
    first_receiver.verify(forward)

    clock_value[0] = NOW + 1
    with pytest.raises(BridgeAuthenticationError, match="clock moved backwards"):
        second_receiver.verify(first)

    # Verification can resume once the shared wall clock reaches its previous high-water mark.
    clock_value[0] = NOW + 31
    recovered = sender.create_request(BridgeAction.STATUS_READ)
    assert second_receiver.verify(recovered) is None


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
    sender = make_authenticator(max_nonces=1)
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



def test_replay_state_registry_is_bounded_and_fails_closed_without_evicting_existing_keys():
    secrets = [
        f"bridge-registry-secret-{index:04d}".ljust(32, "x")
        for index in range(MAX_REPLAY_STATES)
    ]
    receivers = [
        BridgeAuthenticator(secret, clock=lambda: NOW)
        for secret in secrets
    ]
    sender = BridgeAuthenticator(secrets[0], clock=lambda: NOW)
    request = sender.create_request(BridgeAction.STATUS_READ)

    receivers[0].verify(request)

    with pytest.raises(ValueError, match="registry is full"):
        BridgeAuthenticator("bridge-registry-secret-overflow".ljust(32, "x"))

    with pytest.raises(BridgeAuthenticationError, match="already been used"):
        receivers[0].verify(request)
    assert len(BridgeAuthenticator._replay_states) == MAX_REPLAY_STATES


def test_per_key_nonce_capacity_has_a_hard_upper_bound():
    with pytest.raises(ValueError, match="max_nonces"):
        make_authenticator(max_nonces=MAX_NONCES_PER_KEY + 1)
