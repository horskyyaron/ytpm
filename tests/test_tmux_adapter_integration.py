# tests/test_tmux_adapter_integration.py

import os
import shutil
import uuid

import pytest

from ytpm.adapters.tmux import TmuxAdapter, TmuxNotFoundError




def tmux_available() -> bool:
    return shutil.which("tmux") is not None


@pytest.fixture
def adapter():
    if not tmux_available():
        pytest.skip("tmux not available, skipping integration tests")
    try:
        return TmuxAdapter()
    except TmuxNotFoundError:
        pytest.skip("tmux not available, skipping integration tests")


@pytest.fixture
def unique_session_name():
    return f"ytpm-test-{uuid.uuid4().hex[:8]}"


def test_create_and_list_session(adapter, unique_session_name, tmp_path):
    cwd = tmp_path.as_posix()
    adapter.create_session(unique_session_name, cwd)

    sessions = adapter.list_sessions()
    assert unique_session_name in sessions

    # cleanup
    adapter.kill_session(unique_session_name)
    assert unique_session_name not in adapter.list_sessions()


def test_session_exists_roundtrip(adapter, unique_session_name, tmp_path):
    cwd = tmp_path.as_posix()
    assert adapter.session_exists(unique_session_name) is False

    adapter.create_session(unique_session_name, cwd)
    assert adapter.session_exists(unique_session_name) is True

    adapter.kill_session(unique_session_name)
    assert adapter.session_exists(unique_session_name) is False
