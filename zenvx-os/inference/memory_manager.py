"""memory_manager.py - circular buffer memory, RAM monitoring, summarization."""
import gc
from collections import deque

try:
    import psutil
    _HAS_PSUTIL = True
except Exception:  # noqa: BLE001
    _HAS_PSUTIL = False


def estimate_tokens(text):
    return max(len(text) // 4, 1)


class MemoryBuffer:
    def __init__(self, max_tokens=2048):
        self.max_tokens = max_tokens
        self.entries = deque()
        self.token_count = 0

    def add(self, text):
        tokens = estimate_tokens(text)
        self.entries.append((text, tokens))
        self.token_count += tokens
        while self.token_count > self.max_tokens and len(self.entries) > 1:
            _, t = self.entries.popleft()
            self.token_count -= t

    def usage(self):
        return self.token_count / self.max_tokens if self.max_tokens else 0.0

    def context_text(self):
        return "\n".join(text for text, _ in self.entries)


class RAMMonitor:
    def __init__(self, max_ram_mb=3072):
        self.max_ram_mb = max_ram_mb

    def rss_mb(self):
        if _HAS_PSUTIL:
            return psutil.Process().memory_info().rss / (1024 * 1024)
        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        return int(line.split()[1]) / 1024
        except OSError:
            pass
        return 0.0

    def maybe_gc(self):
        if self.rss_mb() > 0.8 * self.max_ram_mb:
            gc.collect()
            return True
        return False


class MemoryManager:
    def __init__(self, config, llm=None):
        hw = config.get("hardware", {})
        self.buffer = MemoryBuffer(hw.get("context_size", 2048))
        self.ram = RAMMonitor(hw.get("max_ram_mb", 3072))
        self.llm = llm

    def add(self, text):
        self.buffer.add(text)
        self.ram.maybe_gc()
        if self.buffer.usage() > 0.8 and self.llm is not None:
            self._summarize()

    def _summarize(self):
        text = self.buffer.context_text()
        summary = self.llm.generate(
            "Summarize the following context concisely:\n" + text)
        self.buffer = MemoryBuffer(self.buffer.max_tokens)
        self.buffer.add("[summary] " + summary)

    def context(self):
        return self.buffer.context_text()

    def recall(self, query):
        q = query.lower()
        hits = [text for text, _ in self.buffer.entries if q in text.lower()]
        return "\n".join(hits) if hits else "No matching memory."
