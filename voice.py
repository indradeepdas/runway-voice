"""Voice layer: AssemblyAI transcription with an offline mock mode.

Real mode uses AssemblyAI's Universal model for file/stream transcription.
Mock mode returns canned transcripts so the full pipeline runs with no API key
(used for offline development and the pre-submission demo build).
"""
import os

MOCK_TRANSCRIPTS = [
    "What is our runway?",
    "Which invoices are overdue?",
    "What happens if we hire an engineer?",
    "What if Helios pays late?",
    "What is our weekly burn?",
]


def transcribe(audio_path=None, mock_index=0):
    """Return the transcript text for an audio file.

    Uses ASSEMBLYAI_API_KEY when set; otherwise falls back to mock mode.
    """
    key = os.environ.get("ASSEMBLYAI_API_KEY")
    if key and audio_path:
        import assemblyai as aai
        aai.settings.api_key = key
        config = aai.TranscriptionConfig(speech_models=["universal"])
        transcript = aai.Transcriber(config=config).transcribe(audio_path)
        if transcript.status == "error":
            raise RuntimeError(f"AssemblyAI transcription failed: {transcript.error}")
        return transcript.text
    return MOCK_TRANSCRIPTS[mock_index % len(MOCK_TRANSCRIPTS)]


def mode():
    return "live (AssemblyAI Universal)" if os.environ.get("ASSEMBLYAI_API_KEY") else "mock (no API key set)"
