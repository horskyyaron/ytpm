# ytpm/core/manager.py

from __future__ import annotations

import os
from typing import Protocol, List

from ytpm.adapters.tmux import TmuxAdapter


class AdapterProtocol(Protocol):
    """Minimal interface Manager needs from an adapter."""

    def list_sessions(self) -> List[str]: ...
    def session_exists(self, name: str) -> bool: ...
    def create_session(self, name: str, cwd: str) -> None: ...
    def attach(self, name: str) -> None: ...
    def switch_client(self, name: str) -> None: ...
    def kill_session(self, name: str) -> None: ...



class Manager:
    """High-level session operations, independent of tmux details.

    This is the "core" API used by CLI and TUI.
    """
    def __init__(self, adapter: AdapterProtocol | None = None) -> None:
        if adapter is None:
            adapter = TmuxAdapter()
        self.adapter = adapter

    # --- public API ---
    def list_sessions(self) -> List[str]:
        """Return a list of existing session names."""
        return self.adapter.list_sessions()

    def create_session(self, name: str, cwd: str) -> None:
        """Create a new session, if it doesn't already exist."""
        if self.adapter.session_exists(name):
            # For now: no-op if exists (you could log or raise instead)
            return
        self.adapter.create_session(name, cwd)

    def goto_session(self, name: str, cwd: str) -> None:
        """Ensure a session exists and then attach/switch to it."""
        if not self.adapter.session_exists(name):
            self.adapter.create_session(name, cwd)

        if self._inside_tmux():
            self.adapter.switch_client(name)
        else:
            self.adapter.attach(name)

    def kill_session(self, name: str) -> None:
        """Kill a session if it exists."""
        if self.adapter.session_exists(name):
            self.adapter.kill_session(name)

    # --- internal helpers ---

    def _inside_tmux(self) -> bool:
        """Return True if we are currently running inside a tmux session."""
        # tmux sets the TMUX environment variable inside sessions
        return "TMUX" in os.environ
