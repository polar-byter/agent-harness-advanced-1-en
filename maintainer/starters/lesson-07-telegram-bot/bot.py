"""Connecting to Telegram: the token, command handlers and long polling."""
import os
from pathlib import Path

import telebot

from bot_logic import HELP, handle_text, read_allowed, summary_reply
from local_llm import load_chat

ROOT = Path(__file__).resolve().parent
JOURNAL = ROOT / 'data' / 'journal.xlsx'
ALLOWED = ROOT / 'data' / 'allowed_users.txt'
# The token lives outside the project folder: it will not end up in an archive, a repository or a code screenshot.
TOKEN_FILE = Path.home() / 'agent-secrets' / 'telegram_token.txt'


def read_token() -> str:
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
    if not token and TOKEN_FILE.is_file():
        token = TOKEN_FILE.read_text(encoding='utf-8').strip()
    if not token:
        raise SystemExit(f'No bot token. Save it to the file {TOKEN_FILE}')
    return token


def main():
    allowed = read_allowed(ALLOWED)
    # threaded=False: messages are handled one at a time, so the model never gets two requests at once.
    bot = telebot.TeleBot(read_token(), threaded=False)

    with load_chat() as model:
        @bot.message_handler(commands=['start', 'help'])
        def send_help(message):
            bot.reply_to(message, HELP)

        @bot.message_handler(commands=['id'])
        def send_id(message):
            bot.reply_to(message, f'Your id: {message.from_user.id}')

        @bot.message_handler(commands=['summary'])
        def send_summary(message):
            if message.from_user.id not in allowed:
                bot.reply_to(message, 'The bulletin is for family members only.')
                return
            bot.send_chat_action(message.chat.id, 'typing')
            bot.reply_to(message, summary_reply(model, JOURNAL))

        @bot.message_handler(content_types=['text'])
        def add_entry(message):
            if message.from_user.id not in allowed:
                bot.reply_to(message, 'I only record mischief from family members. You can find your number with /id.')
                return
            bot.send_chat_action(message.chat.id, 'typing')
            author = message.from_user.first_name or 'no name'
            try:
                reply = handle_text(model, JOURNAL, author, message.text)
            except ValueError as error:
                reply = f'Could not sort the entry: {error}'
            except PermissionError:
                reply = 'Cannot save the journal: close journal.xlsx in Excel and send the entry again.'
            bot.reply_to(message, reply)

        print('Bot started, allowed users:', len(allowed))
        print('To stop: the red Stop square in the Run window.')
        bot.infinity_polling()


if __name__ == '__main__':
    main()
