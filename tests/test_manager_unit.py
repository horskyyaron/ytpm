# tests/test_manager_unit.py

from typing import List

import pytest

from ytpm.core.manager import Manager


class FakeAdapter:
    """
    In-memory fake that imitates the TmuxAdapter interface.

    This lets us test Manager without calling real tmux.
    """

    def __init__(self) -> None:
        # Represent sessions as a simple set of names
        self.sessions: set[str] = set()
        # Track calls for attach/switch so we can assert behavior
        self.attach_calls: list[str] = []
        self.switch_calls: list[str] = []

    # --- methods that mimic TmuxAdapter ---

    def list_sessions(self) -> List[str]:
        return sorted(self.sessions)

    def session_exists(self, name: str) -> bool:
        return name in self.sessions

    def create_session(self, name: str, cwd: str) -> None:
        # We don't care about cwd here; just track the session name
        self.sessions.add(name)

    def attach(self, name: str) -> None:
        self.attach_calls.append(name)

    def switch_client(self, name: str) -> None:
        self.switch_calls.append(name)

    def kill_session(self, name: str) -> None:
        self.sessions.discard(name)


def test_list_sessions_returns_adapter_sessions():
    fake = FakeAdapter()
    fake.sessions = {"a", "b"}

    manager = Manager(adapter=fake)
    sessions = manager.list_sessions()

    assert sessions == ["a", "b"]


def test_create_session_does_not_duplicate_existing():
    fake = FakeAdapter()
    fake.sessions = {"existing"}

    manager = Manager(adapter=fake)
    manager.create_session("existing", "/tmp")

    # Still only one session with that name
    assert fake.sessions == {"existing"}


def test_create_session_adds_new_session():
    fake = FakeAdapter()

    manager = Manager(adapter=fake)
    manager.create_session("proj", "/tmp")

    assert "proj" in fake.sessions


def test_goto_session_outside_tmux_creates_and_attaches(monkeypatch: pytest.MonkeyPatch):
    fake = FakeAdapter()
    manager = Manager(adapter=fake)

    # Pretend we are outside tmux
    monkeypatch.setattr(manager, "_inside_tmux", lambda: False)

    manager.goto_session("proj", "/tmp")

    # Session created
    assert "proj" in fake.sessions
    # attach() was called (because we're "outside" tmux)
    assert fake.attach_calls == ["proj"]
    # switch_client() should not be called
    assert fake.switch_calls == []


def test_goto_session_inside_tmux_creates_and_switches(monkeypatch: pytest.MonkeyPatch):
    fake = FakeAdapter()
    manager = Manager(adapter=fake)

    # Pretend we are inside tmux
    monkeypatch.setattr(manager, "_inside_tmux", lambda: True)

    manager.goto_session("proj", "/tmp")

    assert "proj" in fake.sessions
    assert fake.switch_calls == ["proj"]
    assert fake.attach_calls == []


def test_kill_session_removes_if_exists():
    fake = FakeAdapter()
    fake.sessions = {"a", "b"}

    manager = Manager(adapter=fake)
    manager.kill_session("a")

    assert fake.sessions == {"b"}


def test_kill_session_no_error_if_missing():
    fake = FakeAdapter()
    fake.sessions = {"a"}

    manager = Manager(adapter=fake)
    manager.kill_session("missing")

    # Session set stays unchanged
    assert fake.sessions == {"a"}
