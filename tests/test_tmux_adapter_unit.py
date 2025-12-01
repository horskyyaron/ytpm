# tests/test_tmux_adapter_unit.py

import subprocess
import pytest

from ytpm.adapters.tmux import TmuxAdapter, TmuxCommandError, TmuxNotFoundError



def test_tmux_not_found(monkeypatch):
    def fake_which(cmd):
        return None

    import shutil
    monkeypatch.setattr(shutil, "which", fake_which)

    with pytest.raises(TmuxNotFoundError):
        TmuxAdapter(binary="tmux")


def test_list_sessions_parses_output(monkeypatch):
    def fake_run(cmd, capture_output, text):
        class Result:
            returncode = 0
            stdout = "s1\ns2\n"
            stderr = ""
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)

    adapter = TmuxAdapter()
    assert adapter.list_sessions() == ["s1", "s2"]


def test_session_exists_true(monkeypatch):
    def fake_run(cmd, capture_output, text):
        class Result:
            returncode = 0
            stdout = ""
            stderr = ""
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)

    adapter = TmuxAdapter()
    assert adapter.session_exists("foo") is True


def test_session_exists_false(monkeypatch):
    def fake_run(cmd, capture_output, text):
        class Result:
            returncode = 1
            stdout = ""
            stderr = "no such session"
        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)

    adapter = TmuxAdapter()
    assert adapter.session_exists("foo") is False
