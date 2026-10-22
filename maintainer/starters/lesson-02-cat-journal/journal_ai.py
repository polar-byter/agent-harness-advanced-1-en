"""Sorting the journal with a local model."""
from collections import Counter

from local_llm import ask

# A short explanation for each category noticeably improves a small model's accuracy.
CATEGORIES = {
    'kitchen': 'stole or tried to steal food',
    'damage': 'spoiled something: tore, broke, knocked over, stained',
    'noise': 'kept people awake, yowled loudly, woke someone up',
    'affection': 'cuddled, purred, slept next to someone',
    'hunting': 'caught insects, birds or toys, chased something',
}
CLASSIFY_RULE = (
    "Choose the category of the cat's mischief from an entry in the family journal. Categories:\n"
    + '\n'.join(f'- {name}: {meaning}' for name, meaning in CATEGORIES.items())
    + '\nSeverity: 1 - a trifle, 2 - noticeable damage, 3 - needs a repair or a new purchase.'
)
SUMMARY_RULE = (
    "You write a playful family bulletin about the mischief of Whiskers the cat, like a news anchor. "
    'Use only the supplied entries and add nothing of your own. '
    'Do not list the entries by date: write connected text of three or four sentences in English.'
)


def classify_entry(model, text: str) -> dict:
    if not text.strip():
        raise ValueError('An empty entry does not need sorting')
    # Describe the allowed answer with a JSON schema and pass the entry to the model.
    raise NotImplementedError('Complete classify_entry in journal_ai.py using the lesson 2 hints')


def process_journal(model, entries: list[dict], on_progress=None) -> list[dict]:
    """We sort the entries one by one: that makes it easier to see which one the model got wrong."""
    results = []
    for number, entry in enumerate(entries, start=1):
        answer = classify_entry(model, entry['text'])
        results.append({**entry, 'category': answer['category'], 'severity': answer['severity']})
        if on_progress:
            on_progress(number, len(entries))
    return results


def count_categories(results: list[dict]) -> dict:
    return dict(Counter(item['category'] for item in results).most_common())


def write_summary(model, results: list[dict]) -> str:
    counts = count_categories(results)
    # We put the subject "Whiskers" in ourselves: otherwise the model mixes up who did it and who wrote it down.
    lines = [f'- Whiskers: {item["text"]} ({item["category"]}; written by {item["author"]})' for item in results]
    data = 'Count by category: ' + str(counts) + '\nWhat the cat did:\n' + '\n'.join(lines)
    return ask(model, SUMMARY_RULE, data, max_tokens=400)
