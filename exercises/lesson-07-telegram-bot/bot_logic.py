"""What the bot replies to messages. There is nothing from Telegram here, so the logic is easy to check."""
from pathlib import Path

from journal_ai import classify_entry, count_categories, write_summary
from journal_io import append_entry, read_classified

HELP = ("I keep the journal of Whiskers the cat's mischief. Tell me what he did, and I will record it with a category. "
        'Commands: /summary - a bulletin of the latest entries, /id - your Telegram number.')
MAX_LENGTH = 500


def read_allowed(path: Path) -> set[int]:
    """Telegram user numbers allowed to write to the journal. Lines starting with # are skipped."""
    if not path.is_file():
        return set()
    lines = path.read_text(encoding='utf-8').splitlines()
    return {int(line.strip()) for line in lines if line.strip() and not line.startswith('#')}


def handle_text(model, journal_path: Path, author: str, text: str) -> str:
    text = text.strip()
    if not text:
        return 'I do not add an empty entry to the journal.'
    if len(text) > MAX_LENGTH:
        return f'The entry is longer than {MAX_LENGTH} characters. Please shorten it.'
    # Sort the entry with the model, add it to the journal and return the reply for the chat.
    raise NotImplementedError('Complete handle_text in bot_logic.py using the lesson 7 hints')


def summary_reply(model, journal_path: Path, last: int = 10) -> str:
    results = read_classified(journal_path)[-last:]
    if not results:
        return 'The journal has no sorted entries yet.'
    return f'Latest entries by category: {count_categories(results)}\n\n' + write_summary(model, results)
