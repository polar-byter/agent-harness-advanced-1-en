"""Creates starter data that is awkward to write by hand.

This script rebuilds the Excel journals. The recording data/call.wav for lesson 6 is synthesized
with the Microsoft Zira voice (Windows System.Speech, 16 kHz, mono) from CALL_TEXT:
run `python maintainer/make_data.py voice` on Windows.
"""
import subprocess
import sys
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent / 'starters'
JOURNAL = [
    ('2026-10-03', 'Mom', 'Stole a meatball from the table while everyone was watching TV'),
    ('2026-10-03', 'Dad', 'Yowled outside the bedroom door at three in the morning'),
    ('2026-10-04', 'Grandma', 'Fell asleep on my lap and purred for a whole hour'),
    ('2026-10-05', 'Emma', "Caught a fly and left it in Dad's slipper"),
    ('2026-10-05', 'Mom', 'Clawed the new living room curtain to shreds'),
    ('2026-10-06', 'Dad', 'Pushed the violet pot off the windowsill, soil all over the floor'),
    ('2026-10-06', 'Emma', 'Chewed through the bag of cat food and ate half of it'),
    ('2026-10-07', 'Grandma', 'Slept on the freshly ironed shirts'),
    ('2026-10-07', 'Dad', 'Chased the laser pointer and ran into the wardrobe'),
    ('2026-10-08', 'Emma', 'Woke everyone at six in the morning demanding breakfast'),
    ('2026-10-08', 'Mom', 'Knocked my favorite mug off the table and it broke'),
    ('2026-10-09', 'Grandma', 'Met me at the door and rubbed against my legs'),
]
CALL_TEXT = ('Hello. My name is Olivia Parker, order number four five one two. '
             'Two weeks ago I bought an electric kettle from you, and yesterday it stopped switching on. '
             'I would like my money back. I still have the receipt. Please call me back after six in the evening.')


def write_journal(path: Path) -> None:
    book = Workbook()
    sheet = book.active
    sheet.title = 'Journal'
    sheet.append(['Date', 'Written by', 'What happened'])
    for row in JOURNAL:
        sheet.append(row)
    for column, width in zip('ABC', (12, 14, 60)):
        sheet.column_dimensions[column].width = width
    path.parent.mkdir(parents=True, exist_ok=True)
    book.save(path)


def write_voice(path: Path) -> None:
    """Synthesize CALL_TEXT with the Windows English voice into a 16 kHz mono WAV file."""
    script = (
        'Add-Type -AssemblyName System.Speech; '
        '$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
        "$s.SelectVoice('Microsoft Zira Desktop'); $s.Rate = -1; "
        '$f = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(16000, '
        '[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono); '
        f"$s.SetOutputToWaveFile('{path}', $f); $s.Speak('{CALL_TEXT}'); $s.Dispose()"
    )
    subprocess.run(['powershell', '-NoProfile', '-Command', script], check=True)


if __name__ == '__main__':
    for lesson in ('lesson-02-cat-journal', 'lesson-07-telegram-bot'):
        write_journal(ROOT / lesson / 'data' / 'journal.xlsx')
    print('Journals written')
    if 'voice' in sys.argv[1:]:
        write_voice(ROOT / 'lesson-06-speech' / 'data' / 'call.wav')
        print('Voice message written')
