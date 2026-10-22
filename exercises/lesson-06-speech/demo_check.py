from pathlib import Path
from types import SimpleNamespace

from speech import read_wav, transcribe

ROOT = Path(__file__).resolve().parent


class ExampleWhisper:
    """A stand-in for Whisper. Segment times are in hundredths of a second, as in pywhispercpp."""

    def __init__(self):
        self.calls = []

    def transcribe(self, audio, **settings):
        self.calls.append(settings)
        return [SimpleNamespace(t0=0, t1=200, text=' Hello.'),
                SimpleNamespace(t0=744, t1=1164, text=' Two weeks ago I bought an electric kettle from you,')]


def check_exercise():
    model = ExampleWhisper()
    lines = transcribe(model, [0.0] * 16000)
    assert model.calls[0].get('language') == 'en', 'Name the speech language: language=en'
    assert lines[0] == '[00:00] Hello.', lines[0]
    assert lines[1].startswith('[00:07] Two weeks'), 'Turn hundredths of a second into minutes and seconds'
    assert len(read_wav(ROOT / 'data' / 'call.wav')) > 16000 * 20, 'The recording is longer than 20 seconds'
    return lines[1]


def main():
    try:
        print('Offline check:', check_exercise())
    except NotImplementedError as error:
        print(error)


if __name__ == '__main__':
    main()
