"""A customer's voice message: Whisper transcription and a request card from the language model."""
import wave
from pathlib import Path

from local_llm import ask

SAMPLE_RATE = 16000  # Whisper expects 16,000 samples per second

CALL_RULE = (
    "From the transcript of an online store customer's voice message, fill in the request card. "
    'name - the first and last name the customer gave; order - the order number; problem - what happened; '
    'callback - when to call back. Write only what is in the transcript. '
    'If the information is missing, leave an empty string.'
)
CALL_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'order': {'type': 'string'},
        'problem': {'type': 'string'},
        'wish': {'type': 'string', 'enum': ['refund', 'exchange', 'repair', 'advice', 'other']},
        'callback': {'type': 'string'},
    },
    'required': ['name', 'order', 'problem', 'wish', 'callback'],
}


def read_wav(path: Path):
    """Read a 16 kHz, mono, 16-bit WAV and turn the samples into numbers from -1 to 1."""
    import numpy
    with wave.open(str(path), 'rb') as sound:
        if (sound.getframerate(), sound.getnchannels(), sound.getsampwidth()) != (SAMPLE_RATE, 1, 2):
            raise ValueError('A WAV file is needed: 16,000 Hz, one channel, 16 bits')
        frames = sound.readframes(sound.getnframes())
    return numpy.frombuffer(frames, dtype=numpy.int16).astype(numpy.float32) / 32768


def transcribe(model, audio) -> list[str]:
    # Recognize the speech and build lines like "[00:03] text".
    raise NotImplementedError('Complete transcribe in speech.py using the lesson 6 hints')


def call_card(chat_model, lines: list[str]) -> dict:
    return ask(chat_model, CALL_RULE, '\n'.join(lines), schema=CALL_SCHEMA, max_tokens=200)
