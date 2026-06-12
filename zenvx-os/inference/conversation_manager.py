"""conversation_manager.py - multi-turn conversation tracking and persistence."""
import json
import os
import time
import uuid

CONV_DIR = "/var/lib/zenvx/conversations"


class ConversationManager:
    def __init__(self, conv_dir=CONV_DIR):
        self.conv_dir = conv_dir
        os.makedirs(self.conv_dir, exist_ok=True)
        self.conversation_id = uuid.uuid4().hex[:12]
        self.turns = []

    def add_turn(self, user_input, thought, action, result, response):
        turn = {
            "turn_id": len(self.turns) + 1,
            "timestamp": time.time(),
            "user_input": user_input,
            "thought": thought,
            "action": action,
            "result": result,
            "response": response,
        }
        self.turns.append(turn)
        self._persist()
        return turn

    def _path(self, conv_id=None):
        cid = conv_id or self.conversation_id
        return os.path.join(self.conv_dir, f"{cid}.json")

    def _persist(self):
        with open(self._path(), "w") as f:
            json.dump({"id": self.conversation_id, "turns": self.turns},
                      f, indent=2)

    def load(self, conv_id):
        with open(self._path(conv_id)) as f:
            data = json.load(f)
        self.conversation_id = data["id"]
        self.turns = data["turns"]
        return self.turns

    def list_conversations(self):
        return sorted(p[:-5] for p in os.listdir(self.conv_dir)
                      if p.endswith(".json"))

    def export_markdown(self, conv_id=None):
        turns = self.turns if conv_id is None else self.load(conv_id)
        lines = [f"# Conversation {self.conversation_id}\n"]
        for t in turns:
            lines.append(f"## Turn {t['turn_id']}")
            lines.append(f"**User:** {t['user_input']}")
            lines.append(f"**Thought:** {t['thought']}")
            lines.append(f"**Action:** {t['action']}")
            lines.append(f"**Response:** {t['response']}\n")
        return "\n".join(lines)

    def get_reasoning_chain(self):
        return [(t["thought"], t["action"]) for t in self.turns]
