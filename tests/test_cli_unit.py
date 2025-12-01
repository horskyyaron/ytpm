# tests/test_cli_unit.py

from __future__ import annotations

from typing import List

import os
import pytest

from ytpm.cli.main import run


class FakeManager:
    """
    Fake Manager used to test CLI behavior without touching tmux.
    """

    def __init__(self) -> None:
        self.sessions: List[str] = []
        self.create_calls: list[tuple[str, str]] = []
        self.goto_calls: list[tuple[str, str]] = []
        self.kill_calls: list[str] = []

    # Methods expected by CLI
    def list_sessions(self) -> List[str]:
        return self.sessions

    def create_session(self, name: str, cwd: str) -> None:
        self.create_calls.append((name, cwd))

    def goto_session(self, name: str, cwd: str) -> None:
        self.goto_calls.append((name, cwd))

    def kill_session(self, name: str) -> None:
        self.kill_calls.append(name)


def test_ls_prints_sessions_in_order(capsys: pytest.CaptureFixture[str]):
    manager = FakeManager()
    manager.sessions = ["b", "a"]

    exit_code = run(["ls"], manager)

    captured = capsys.readouterr()
    # One per line
    lines = captured.out.strip().splitlines()
    assert exit_code == 0
    assert lines == ["b", "a"]


def test_new_calls_manager_create_with_default_cwd(monkeypatch: pytest.MonkeyPatch):
    manager = FakeManager()

    # Freeze cwd so test is deterministic
    monkeypatch.setenv("PWD", "/tmp/fake")  # just in case
    monkeypatch.chdir("/tmp")  # pytest provides a tmp_path too, but this is fine

    exit_code = run(["new", "proj"], manager)

    assert exit_code == 0
    assert manager.create_calls == [("proj", os.getcwd())]


def test_new_uses_path_if_provided(tmp_path,):
    manager = FakeManager()
    path = tmp_path / "proj"
    path.mkdir()

    exit_code = run(["new", "proj", "--path", str(path)], manager)

    assert exit_code == 0
    assert manager.create_calls == [("proj", str(path))]


def test_goto_calls_manager_goto_with_default_cwd(monkeypatch: pytest.MonkeyPatch):
    manager = FakeManager()

    monkeypatch.chdir("/tmp")

    exit_code = run(["goto", "proj"], manager)

    assert exit_code == 0
    assert manager.goto_calls == [("proj", os.getcwd())]


def test_kill_calls_manager_kill():
    manager = FakeManager()

    exit_code = run(["kill", "proj"], manager)

    assert exit_code == 0
    assert manager.kill_calls == ["proj"]
