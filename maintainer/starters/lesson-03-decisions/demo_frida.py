"""The same requests and questions for the open model FRIDA-Decisions on your CPU."""
import time
from pathlib import Path

from decisions import print_report, read_json
from frida_client import ask_frida, load_frida

ROOT = Path(__file__).resolve().parent
# FRIDA computes confidence differently from ask_choice, so its threshold is chosen again.
THRESHOLD = 0.9


def main():
    try:
        requests = read_json(ROOT / 'data' / 'requests.json')
        questions = read_json(ROOT / 'data' / 'questions.json')
        judge = load_frida()
        started = time.perf_counter()
        results = [(request, ask_frida(judge, request['text'], questions)) for request in requests]
        seconds = time.perf_counter() - started
        print_report(results, THRESHOLD)
        print(f'On average {seconds / len(requests):.1f} s per request')
    except ModuleNotFoundError:
        print('The frida-decisions library is not installed: the install command is at the top of frida_client.py')
    except (ValueError, OSError) as error:
        print(error)


if __name__ == '__main__':
    main()
