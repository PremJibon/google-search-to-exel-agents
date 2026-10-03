import sys
import os
import io
import wave

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

from src.services.voice_service import voice_service

print("Testing VoiceService availability...")
assert voice_service.is_available(), "VoiceService should be available with valid GROQ_API_KEY"

# Create a small valid WAV in-memory
buf = io.BytesIO()
with wave.open(buf, 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(16000)
    w.writeframes(b'\x00' * 32000)
buf.seek(0)

print("Calling voice_service.transcribe_audio()...")
result = voice_service.transcribe_audio(buf, filename="test.wav")

print("Result success:", result["success"])
print("Result duration:", result["duration_ms"], "ms")
print("Result text (filtered silence):", repr(result["text"]))
assert result["success"] is True, "Transcription request should succeed"
print("VoiceService test PASSED successfully!")
