"""llm_engine.py - LLM inference wrapper around llama-cpp-python with mock fallback."""
import os
import time

try:
    from llama_cpp import Llama
    _HAS_LLAMA = True
except Exception:  # noqa: BLE001
    _HAS_LLAMA = False


class LLMEngine:
    def __init__(self, config):
        self.config = config
        hw = config.get("hardware", {})
        perf = config.get("performance", {})
        self.model_path = config.get("models", {}).get("llm", "")
        self.threads = hw.get("inference_threads", 4)
        self.context_size = hw.get("context_size", 2048)
        self.gpu_layers = hw.get("gpu_layers", 0)
        self.max_tokens = perf.get("max_tokens", 512)
        self.llm = None
        self._load()

    def _load(self):
        if _HAS_LLAMA and self.model_path and os.path.exists(self.model_path):
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.context_size,
                n_threads=self.threads,
                n_gpu_layers=self.gpu_layers,
                verbose=False,
            )
        else:
            self.llm = None  # mock mode

    def generate(self, prompt, stream=False):
        """Return a completion string. Logs tokens/sec."""
        start = time.time()
        if self.llm is None:
            text = self._mock(prompt)
            tokens = max(len(text.split()), 1)
        else:
            out = self.llm(
                prompt,
                max_tokens=self.max_tokens,
                stream=False,
                stop=["</s>", "\nUser:"],
            )
            text = out["choices"][0]["text"]
            tokens = out.get("usage", {}).get("completion_tokens",
                                              len(text.split()))
        elapsed = max(time.time() - start, 1e-6)
        self.last_tps = tokens / elapsed
        return text.strip()

    def stream_tokens(self, prompt):
        """Yield tokens as they are produced."""
        if self.llm is None:
            for word in self._mock(prompt).split():
                yield word + " "
            return
        for chunk in self.llm(prompt, max_tokens=self.max_tokens, stream=True):
            yield chunk["choices"][0]["text"]

    def _mock(self, prompt):
        return (
            '{"thought": "Model file not found; running in mock mode.", '
            '"action": "respond", '
            '"parameters": {"text": "ZenvX is running without a model loaded. '
            'Download a model via first-boot setup."}, '
            '"confidence": 0.5}'
        )
