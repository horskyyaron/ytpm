from __future__ import annotations

import shutil
import subprocess
from typing import List


class TmuxNotFoundError(RuntimeError):
    """Raised when tmux binary is not available on PATH."""


class TmuxCommandError(RuntimeError):
    """Raised when a tmux command fails."""

    def __init__(self, command: list[str], stderr: str, returncode: int) -> None:
        self.command = command
        self.stderr = stderr
        self.returncode = returncode
        message = f"tmux command failed ({returncode}): {' '.join(command)}\n{stderr}"
        super().__init__(message)


class TmuxAdapter:
    """Thin wrapper around the tmux CLI."""

    def __init__(self, binary: str = "tmux") -> None:
        self.binary = binary
        self._ensure_tmux_available()

    def _ensure_tmux_available(self) -> None:
        if shutil.which(self.binary) is None:
            raise TmuxNotFoundError(
                f"'{self.binary}' not found on PATH. Please install tmux."
            )

    def _run(self, *args: str) -> str:
        cmd = [self.binary, *args]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise TmuxCommandError(cmd, proc.stderr.strip(), proc.returncode)
        return proc.stdout.strip()

    # --- public API ---
    def list_sessions(self) -> List[str]:
        """Return a list of session names.

        If no tmux server is running, return an empty list.
        """
        try:
            output = self._run("list-sessions", "-F", "#S")
        except TmuxCommandError as e:
            # When there is no server, tmux exits with code 1 and this stderr:
            # "no server running on /tmp/tmux-XXXX/default"
            if "no server running" in e.stderr:
                return []
            # Any other tmux error should still bubble up
            raise

        if not output:
            return []
        return output.splitlines()


    def session_exists(self, name: str) -> bool:
        """Return True if a session with the given name exists."""
        try:
            self._run("has-session", "-t", name)
            return True
        except TmuxCommandError:
            return False

    def create_session(self, name: str, cwd: str) -> None:
        """Create a new detached session with the given name and working directory. tmux is running"""
        self._run("new-session", "-d", "-s", name, "-c", cwd)

    def attach(self, name: str) -> None:
        """Attach to the given session (used when outside tmux)."""
        self._run("attach", "-t", name)

    def switch_client(self, name: str) -> None:
        """Switch the current tmux client to the given session (used inside tmux)."""
        self._run("switch-client", "-t", name)  

    def kill_session(self, name: str) -> None:
        """Kill the given tmux session."""
        self._run("kill-session", "-t", name)  
