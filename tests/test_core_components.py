from jarvis.core.command_engine import Command, CommandEngine, CommandResult
from jarvis.core.event_bus import EventBus
from jarvis.core.events import Event
from jarvis.core.guardian import GuardianMonitor


def test_event_bus_dispatch_and_unsubscribe():
    bus = EventBus()
    received = []
    unsubscribe = bus.subscribe("demo", received.append)

    assert bus.publish(Event("demo", {"value": 7})) == 1
    assert received[0].payload["value"] == 7

    unsubscribe()
    assert bus.publish(Event("demo")) == 0


def test_event_bus_wildcard_subscription():
    bus = EventBus()
    received = []
    bus.subscribe("*", received.append)

    assert bus.publish(Event("system.ready")) == 1
    assert received[0].name == "system.ready"


def test_command_engine_only_runs_registered_commands():
    engine = CommandEngine()
    assert engine.execute("status").ok
    assert not engine.execute("not-a-command").ok
    assert not engine.execute("status anything").ok
    assert engine.execute("exit").should_exit


def test_command_registration_rejects_duplicates():
    engine = CommandEngine()
    try:
        engine.register(Command("status", "duplicate", lambda: CommandResult(True, "bad")))
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate command should be rejected")


def test_guardian_emits_failure_after_threshold_and_recovery():
    bus = EventBus()
    events = []
    bus.subscribe("*", events.append)
    healthy = {"value": False}
    guardian = GuardianMonitor(bus, failure_threshold=2)
    guardian.register_check("sample", lambda: healthy["value"])

    assert guardian.run_once()[0].consecutive_failures == 1
    assert guardian.run_once()[0].consecutive_failures == 2
    assert any(event.name == "guardian.check_failed" for event in events)

    healthy["value"] = True
    assert guardian.run_once()[0].consecutive_failures == 0
    assert events[-1].name == "guardian.check_recovered"
