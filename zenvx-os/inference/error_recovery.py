"""error_recovery.py - retry with exponential backoff and a circuit breaker."""
import time


class CircuitBreaker:
    def __init__(self, max_failures=3, reset_timeout=60):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self._failures = {}
        self._opened_at = {}

    def is_open(self, key):
        if key in self._opened_at:
            if time.time() - self._opened_at[key] > self.reset_timeout:
                self._failures[key] = 0
                del self._opened_at[key]
                return False
            return True
        return False

    def record_failure(self, key):
        self._failures[key] = self._failures.get(key, 0) + 1
        if self._failures[key] >= self.max_failures:
            self._opened_at[key] = time.time()

    def record_success(self, key):
        self._failures[key] = 0
        self._opened_at.pop(key, None)


class ErrorRecovery:
    FATAL = (KeyboardInterrupt, SystemExit, MemoryError)

    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.breaker = CircuitBreaker()

    def is_recoverable(self, exc):
        return not isinstance(exc, self.FATAL)

    def execute_with_retry(self, func, *args, key="default", fallback=None,
                           **kwargs):
        if self.breaker.is_open(key):
            if fallback:
                return fallback(*args, **kwargs)
            raise RuntimeError(f"Circuit open for {key}")
        delay = self.base_delay
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                self.breaker.record_success(key)
                return result
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if not self.is_recoverable(exc):
                    raise
                self.breaker.record_failure(key)
                if attempt < self.max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
        if fallback:
            return fallback(*args, **kwargs)
        raise last_exc
