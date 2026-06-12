"""undo_manager.py - stack of undoable actions."""
from collections import deque


class UndoManager:
    def __init__(self, max_history=20):
        self.max_history = max_history
        self.stack = deque(maxlen=max_history)

    def push(self, name, undo_callable, description=""):
        self.stack.append({"name": name, "undo": undo_callable,
                           "description": description})

    def undo(self):
        if not self.stack:
            return "Nothing to undo."
        entry = self.stack.pop()
        try:
            entry["undo"]()
            return f"Undid: {entry['name']} ({entry['description']})"
        except Exception as exc:  # noqa: BLE001
            return f"Undo failed for {entry['name']}: {exc}"

    def depth(self):
        return len(self.stack)
