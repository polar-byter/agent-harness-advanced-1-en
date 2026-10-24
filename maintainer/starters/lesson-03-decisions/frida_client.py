"""The same questions for the open decision model FRIDA-Decisions from Sber: it runs on the CPU without a network.

The library is installed separately, only this variant of the lesson needs it:
python -m pip install --only-binary=:all: "frida-decisions[onnx] @ https://github.com/ai-forever/FRIDA-Decisions/archive/refs/tags/v0.4.0.zip"
It is imported inside load_frida, so the offline checks work without the library.
"""
from local_llm import models_dir

REPO = 'ai-forever/FRIDA-Decisions'
# For the CPU we need the model settings and the ONNX graph compressed to 8 bits, about 1.2 GB.
FILES = ['*.json', 'onnx/*']


def frida_dir():
    return models_dir() / 'FRIDA-Decisions'


def load_frida(threads: int = 4):
    """Download the missing files into the shared models folder and load the model."""
    from huggingface_hub import snapshot_download
    from frida_decisions import OnnxJudge

    folder = frida_dir()
    print('FRIDA-Decisions: checking files in', folder, '(the first run downloads about 1.2 GB)')
    snapshot_download(REPO, allow_patterns=FILES, local_dir=folder)
    return OnnxJudge.from_pretrained(folder, threads=threads)


def ask_frida(judge, state: str, questions: dict) -> dict:
    """A request in the same format as Jev's, and answers with the same keys as decide."""
    return judge.judge({'state': state, 'questions': questions})['answers']
