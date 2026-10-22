"""A conversation with the bot without Telegram: the same functions bot.py calls, with messages set in code."""
import shutil
from pathlib import Path

from bot_logic import handle_text, summary_reply
from demo_check import check_exercise
from local_llm import load_chat

ROOT = Path(__file__).resolve().parent


def main():
    try:
        check_exercise()
        journal = ROOT / 'data' / 'demo-journal.xlsx'
        shutil.copy(ROOT / 'data' / 'journal.xlsx', journal)
        with load_chat() as model:
            for author, text in [('Emma', 'Grabbed a sausage off the table while I was pouring tea'),
                                 ('Dad', 'Knocked my headphones off the shelf, an ear cushion broke off')]:
                print(f'{author}: {text}')
                print('Bot:', handle_text(model, journal, author, text))
            print('Bot on /summary:', summary_reply(model, journal))
    except (NotImplementedError, FileNotFoundError, ModuleNotFoundError, ValueError) as error:
        print(error)


if __name__ == '__main__':
    main()
