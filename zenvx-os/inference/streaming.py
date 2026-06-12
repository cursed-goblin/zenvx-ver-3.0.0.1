"""streaming.py - token streaming handler."""
import sys


class StreamHandler:
    def __init__(self, token_iter):
        self.token_iter = token_iter
        self.callbacks = []

    def on_token(self, callback):
        self.callbacks.append(callback)
        return self

    def run(self, echo=True):
        parts = []
        for token in self.token_iter:
            parts.append(token)
            if echo:
                sys.stdout.write(token)
                sys.stdout.flush()
            for cb in self.callbacks:
                cb(token)
        if echo:
            sys.stdout.write("\n")
            sys.stdout.flush()
        return "".join(parts)
