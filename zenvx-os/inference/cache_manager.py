"""cache_manager.py - two-tier (memory + disk) cache with TTL and stats."""
import hashlib
import json
import os
import time

CACHE_DIR = "/var/lib/zenvx/cache"


class CacheManager:
    def __init__(self, cache_dir=CACHE_DIR, default_ttl=3600):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        os.makedirs(self.cache_dir, exist_ok=True)
        self._l1 = {}
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0

    @staticmethod
    def _key(raw):
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def _path(self, key):
        return os.path.join(self.cache_dir, key + ".json")

    def get(self, raw):
        key = self._key(raw)
        now = time.time()
        if key in self._l1:
            value, expiry = self._l1[key]
            if expiry > now:
                self.l1_hits += 1
                return value
            del self._l1[key]
        path = self._path(key)
        if os.path.exists(path):
            try:
                with open(path) as f:
                    rec = json.load(f)
                if rec["expiry"] > now:
                    self.l2_hits += 1
                    self._l1[key] = (rec["value"], rec["expiry"])
                    return rec["value"]
                os.remove(path)
            except (OSError, ValueError):
                pass
        self.misses += 1
        return None

    def set(self, raw, value, ttl=None):
        key = self._key(raw)
        expiry = time.time() + (ttl or self.default_ttl)
        self._l1[key] = (value, expiry)
        try:
            with open(self._path(key), "w") as f:
                json.dump({"value": value, "expiry": expiry}, f)
        except OSError:
            pass

    def stats(self):
        total = self.l1_hits + self.l2_hits + self.misses
        hit_rate = (self.l1_hits + self.l2_hits) / total if total else 0.0
        return {"l1_hits": self.l1_hits, "l2_hits": self.l2_hits,
                "misses": self.misses, "hit_rate": round(hit_rate, 3)}
