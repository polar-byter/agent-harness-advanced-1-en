"""Reading and writing the journal in Excel. No model is used here."""
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook

HEADER = ['Date', 'Written by', 'What happened']
RESULT_SHEET = 'Review'


def as_text(value) -> str:
    if isinstance(value, (datetime, date)):
        return value.strftime('%Y-%m-%d')
    return '' if value is None else str(value).strip()


def read_journal(path: Path) -> list[dict]:
    """First sheet: date, author of the entry and text. Rows without text are skipped."""
    book = load_workbook(path, read_only=True)
    sheet = book.worksheets[0]
    entries = []
    for row in sheet.iter_rows(min_row=2, max_col=3, values_only=True):
        when, author, text = (as_text(value) for value in row)
        if text:
            entries.append({'date': when, 'author': author, 'text': text})
    book.close()
    return entries


def save_results(path: Path, results: list[dict], summary: str) -> None:
    """Recreate the review sheet; the original journal sheet stays untouched."""
    book = load_workbook(path)
    if RESULT_SHEET in book.sheetnames:
        del book[RESULT_SHEET]
    sheet = book.create_sheet(RESULT_SHEET)
    sheet.append(HEADER + ['Category', 'Severity'])
    for item in results:
        sheet.append([item['date'], item['author'], item['text'], item['category'], item['severity']])
    sheet.append([])
    sheet.append(['Family bulletin', '', summary])
    for column, width in zip('ABCDE', (12, 14, 60, 12, 12)):
        sheet.column_dimensions[column].width = width
    book.save(path)


def append_entry(path: Path, author: str, text: str, extra: tuple = ()) -> None:
    """Add an entry to the end of the journal; if the file is missing, create it with a header.

    extra can carry the category and severity straight away: they go into columns D and E.
    """
    if path.is_file():
        book = load_workbook(path)
    else:
        book = Workbook()
        book.active.title = 'Journal'
        book.active.append(HEADER)
    book.worksheets[0].append([date.today().strftime('%Y-%m-%d'), author, text, *extra])
    book.save(path)


def read_classified(path: Path) -> list[dict]:
    """Entries that already have a category and severity in columns D and E."""
    book = load_workbook(path, read_only=True)
    entries = []
    for row in book.worksheets[0].iter_rows(min_row=2, max_col=5, values_only=True):
        when, author, text, category, severity = (list(row) + [None] * 5)[:5]
        if text and category:
            entries.append({'date': as_text(when), 'author': as_text(author), 'text': as_text(text),
                            'category': as_text(category), 'severity': severity})
    book.close()
    return entries
