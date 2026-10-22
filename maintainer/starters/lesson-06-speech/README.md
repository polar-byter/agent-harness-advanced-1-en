# A customer's voice message

Whisper transcribes the recording on the processor, and the language model fills in a request card
from the transcript. The training recording data/call.wav was synthesized with a Windows voice.

1. Open this folder in PyCharm with File -> Open and choose the shared course interpreter.
2. Install the dependencies: `python -m pip install --only-binary=:all: -r requirements.txt`.
3. Run get_models.py: it downloads Whisper small, about 490 MB.
4. Complete transcribe in speech.py using TASK.md.
5. Run demo_check.py, then demo.py.

Once transcribe is done, demo_check.py prints:

```text
Offline check: [00:07] Two weeks ago I bought an electric kettle from you,
```

Checks: tests/test_lesson.py -> class LessonTests -> Run.
