import json
import shutil
import tempfile
from pathlib import Path

from bot_logic import handle_text
from journal_io import read_classified

ROOT = Path(__file__).resolve().parent
TEXT = 'Grabbed a sausage off the table'


class ExampleModel:
    """A stand-in for the model: files any entry under kitchen."""

    def __init__(self):
        self.calls = []

    def create_chat_completion(self, **settings):
        self.calls.append(settings)
        content = json.dumps({'category': 'kitchen', 'severity': 1})
        return {'choices': [{'finish_reason': 'stop', 'message': {'content': content}}]}


def check_exercise():
    # Work on a copy of the journal, so the check does not change data/journal.xlsx.
    with tempfile.TemporaryDirectory() as folder:
        journal = Path(folder) / 'journal.xlsx'
        shutil.copy(ROOT / 'data' / 'journal.xlsx', journal)
        model = ExampleModel()
        reply = handle_text(model, journal, 'Emma', TEXT)
        assert model.calls, 'Pass the entry to the model through classify_entry'
        saved = read_classified(journal)
        assert saved and saved[-1]['text'] == TEXT, 'Add the entry to the journal together with its category'
        assert saved[-1]['author'] == 'Emma' and saved[-1]['category'] == 'kitchen'
    return reply


def main():
    try:
        print('Offline check:', check_exercise())
    except NotImplementedError as error:
        print(error)


if __name__ == '__main__':
    main()
