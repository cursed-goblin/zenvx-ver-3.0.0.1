"""persistence.py - save and restore agent state as JSON."""
import json
import os
import time

STATE_PATH = "/var/lib/zenvx/agent_state.json"


class Persistence:
    def __init__(self, path=STATE_PATH):
        self.path = path

    def save(self, state):
        record = dict(state)
        record["_saved_at"] = time.time()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(record, f, indent=2)

    def load(self):
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path) as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}
