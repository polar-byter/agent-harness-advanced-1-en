from pathlib import Path
from time import perf_counter

from demo_check import check_exercise
from local_llm import load_chat, load_speech
from speech import call_card, read_wav, transcribe

ROOT = Path(__file__).resolve().parent


def main():
    try:
        check_exercise()
        audio = read_wav(ROOT / 'data' / 'call.wav')
        print(f'Recording length: {len(audio) / 16000:.1f} s')
        with load_speech() as model:
            start = perf_counter()
            lines = transcribe(model, audio)
            print(f'Transcribed in {perf_counter() - start:.1f} s:')
            print('\n'.join(lines))
        with load_chat() as chat_model:
            print('Request card:', call_card(chat_model, lines))
    except (NotImplementedError, FileNotFoundError, ModuleNotFoundError, ValueError) as error:
        print(error)


if __name__ == '__main__':
    main()
