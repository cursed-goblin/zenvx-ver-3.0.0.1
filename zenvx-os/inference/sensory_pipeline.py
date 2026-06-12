"""sensory_pipeline.py - screen capture, vision description, and speech to text."""
import os
import tempfile

try:
    import mss
    _HAS_MSS = True
except Exception:  # noqa: BLE001
    _HAS_MSS = False

try:
    from PIL import Image
    _HAS_PIL = True
except Exception:  # noqa: BLE001
    _HAS_PIL = False


class SensoryPipeline:
    def __init__(self, config=None):
        self.config = config or {}
        self._whisper = None
        self._moondream = None

    def capture_screen(self, path=None):
        if not (_HAS_MSS and _HAS_PIL):
            return {"error": "screen capture unavailable (mss/Pillow missing)"}
        path = path or os.path.join(tempfile.gettempdir(), "zenvx_screen.png")
        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[0])
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            img.save(path)
        return {"path": path, "size": img.size}

    def describe_image(self, path):
        try:
            import moondream as md
            if self._moondream is None:
                self._moondream = md.vl(model="moondream2")
            from PIL import Image as PILImage
            image = PILImage.open(path)
            enc = self._moondream.encode_image(image)
            return self._moondream.query(enc, "Describe this screen.")["answer"]
        except Exception as exc:  # noqa: BLE001
            return f"vision unavailable: {exc}"

    def transcribe(self, audio_path):
        try:
            from faster_whisper import WhisperModel
            if self._whisper is None:
                self._whisper = WhisperModel("base", compute_type="int8")
            segments, _ = self._whisper.transcribe(audio_path)
            return " ".join(seg.text for seg in segments).strip()
        except Exception as exc:  # noqa: BLE001
            return f"stt unavailable: {exc}"

    def record_microphone(self, seconds=5, path=None):
        try:
            import sounddevice as sd
            import soundfile as sf
            path = path or os.path.join(tempfile.gettempdir(), "zenvx_mic.wav")
            rate = 16000
            audio = sd.rec(int(seconds * rate), samplerate=rate, channels=1)
            sd.wait()
            sf.write(path, audio, rate)
            return path
        except Exception as exc:  # noqa: BLE001
            return f"recording unavailable: {exc}"
