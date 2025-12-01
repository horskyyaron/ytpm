from __future__ import annotations

import os
from typing import List, Optional, Tuple

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label
from textual.binding import Binding

from ytpm.core.manager import Manager


class SessionItem(ListItem):
    """List item representing a single tmux session."""

    def __init__(self, session_name: str) -> None:
        super().__init__(Label(session_name))
        self.session_name = session_name


class YtpmTui(App[Optional[Tuple[str, str]]]):
    """
    Simple TUI that lists sessions and lets the user pick one.

    When the user confirms a selection, the app exits with a result:
    (session_name, cwd).
    """

    BINDINGS = [
        Binding("q", "quit_app", "Quit"),
        Binding("r", "reload_sessions", "Reload"),
        Binding("enter", "select_session", "Attach/switch"),
    ]

    def __init__(self, manager: Optional[Manager] = None) -> None:
        super().__init__()
        self.manager = manager or Manager()
        self._list_view: Optional[ListView] = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        self._list_view = ListView()
        yield self._list_view
        yield Footer()

    async def on_mount(self) -> None:
        await self._reload_sessions()


    async def _reload_sessions(self) -> None:
        assert self._list_view is not None
        self._list_view.clear()

        sessions: List[str] = self.manager.list_sessions()
        for name in sessions:
            self._list_view.append(SessionItem(name))

        if sessions:
            self._list_view.focus()  # ← no await here
        else:
            # No sessions yet; you can still select a name via CLI later
            pass
        # --- Actions (bound to keys via BINDINGS) ---

    async def action_quit_app(self) -> None:
        """Quit without selecting a session."""
        self.exit(None)

    async def action_reload_sessions(self) -> None:
        """Reload the list of sessions."""
        await self._reload_sessions()

    async def action_select_session(self) -> None:
        """Confirm the currently selected session and exit with its name."""
        assert self._list_view is not None

        if self._list_view.index is None:
            return  # nothing selected

        item = self._list_view.children[self._list_view.index]
        if not isinstance(item, SessionItem):
            return

        session_name = item.session_name
        cwd = os.getcwd()
        # Exit the app and return (name, cwd) to the caller of app.run()
        self.exit((session_name, cwd))

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Called when the user presses Enter on a list item."""
        item = event.item
        if not isinstance(item, SessionItem):
            return

        session_name = item.session_name
        cwd = os.getcwd()
        # Exit the TUI and return (session_name, cwd) to run_tui()
        self.exit((session_name, cwd))


def run_tui(manager: Optional[Manager] = None) -> None:
    """
    Entry point to run the TUI and then attach/switch to the chosen session.

    - If the user cancels (q), do nothing.
    - If the user selects a session, we call manager.goto_session(name, cwd).
    """
    mgr = manager or Manager()
    app = YtpmTui(manager=mgr)
    result = app.run()

    if result is None:
        # User quit without selecting a session
        return

    session_name, cwd = result
    mgr.goto_session(session_name, cwd)
