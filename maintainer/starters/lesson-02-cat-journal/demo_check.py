import json
from pathlib import Path

from journal_ai import CATEGORIES, classify_entry, process_journal
from journal_io import read_journal

ROOT = Path(__file__).resolve().parent
TEXT = 'Stole a meatball from the table while everyone was watching TV'


class ExampleModel:
    """A stand-in for the model: picks a prepared answer by a keyword."""
    ANSWERS = {'meatball': ('kitchen', 1), 'curtain': ('damage', 2), 'yowled': ('noise', 1)}

    def __init__(self):
        self.calls = []

    def create_chat_completion(self, **settings):
        self.calls.append(settings)
        text = settings['messages'][1]['content']
        category, severity = next((value for key, value in self.ANSWERS.items() if key in text), ('affection', 1))
        content = json.dumps({'category': category, 'severity': severity})
        return {'choices': [{'finish_reason': 'stop', 'message': {'content': content}}]}


def check_exercise():
    model = ExampleModel()
    answer = classify_entry(model, TEXT)
    settings = model.calls[0]
    assert settings['messages'][1]['content'] == TEXT, 'Pass the entry text to the model'
    schema = settings.get('response_format', {}).get('schema', {})
    assert schema['properties']['category']['enum'] == list(CATEGORIES), 'Take the schema categories from CATEGORIES'
    assert answer == {'category': 'kitchen', 'severity': 1}, answer
    results = process_journal(ExampleModel(), read_journal(ROOT / 'data' / 'journal.xlsx'))
    assert len(results) == 12, 'The training journal has 12 entries'
    return f'{TEXT} -> {answer["category"]}, severity {answer["severity"]}'


def main():
    try:
        print('Offline check:', check_exercise())
    except NotImplementedError as error:
        print(error)


if __name__ == '__main__':
    main()
