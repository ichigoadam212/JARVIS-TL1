import pytest

from jarvis.core.guardian import RestartSupervisor


def test_restart_supervisor_allows_first_attempt_and_applies_backoff():
    supervisor = RestartSupervisor()

    assert supervisor.can_restart(now=0)
    state = supervisor.record_failure(now=10)
    assert state.attempts == 1
    assert not supervisor.can_restart(now=10.99)
    assert supervisor.can_restart(now=11)


def test_restart_supervisor_uses_exponential_backoff_and_cap():
    supervisor = RestartSupervisor(max_attempts=5, base_backoff_seconds=1, max_backoff_seconds=3)

    supervisor.record_failure(now=0)
    assert supervisor.can_restart(now=1)
    supervisor.record_failure(now=1)
    assert not supervisor.can_restart(now=2.99)
    assert supervisor.can_restart(now=3)
    supervisor.record_failure(now=3)
    assert not supervisor.can_restart(now=4.99)
    assert supervisor.can_restart(now=6)


def test_restart_supervisor_stops_at_attempt_limit():
    supervisor = RestartSupervisor(max_attempts=2)

    supervisor.record_failure(now=0)
    supervisor.record_failure(now=1)
    state = supervisor.record_failure(now=2)

    assert state.attempts == 2
    assert not state.allowed
    assert not supervisor.can_restart(now=1000)


def test_healthy_run_resets_failure_history():
    supervisor = RestartSupervisor(max_attempts=2)

    supervisor.record_failure(now=0)
    supervisor.record_failure(now=1)
    assert not supervisor.can_restart(now=100)

    state = supervisor.record_healthy_run()
    assert state.attempts == 0
    assert state.last_failure_at is None
    assert state.allowed
    assert state.retry_after_seconds == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_attempts": 0},
        {"base_backoff_seconds": 0},
        {"max_backoff_seconds": 0.5, "base_backoff_seconds": 1},
    ],
)
def test_restart_supervisor_rejects_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        RestartSupervisor(**kwargs)
