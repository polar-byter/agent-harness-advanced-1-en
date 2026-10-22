# A Telegram bot for the cat journal

The bot receives messages about the cat's mischief from family members, sorts them with a local model
and writes them to the same Excel journal as the utility from lesson 2.

```text
bot_logic.py   what to reply to a message; nothing from Telegram here
bot.py         connecting to Telegram: token, handlers, long polling
journal_ai.py  sorting an entry with the model (ready from lesson 2)
journal_io.py  reading and writing Excel (ready from lesson 2)
```

1. Open this folder in PyCharm with File -> Open and choose the shared course interpreter.
2. Install the dependencies: `python -m pip install --only-binary=:all: -r requirements.txt`.
3. Complete handle_text in bot_logic.py using TASK.md.
4. Run demo_check.py, then demo.py: this is a conversation with the bot without Telegram.
5. Create a bot with @BotFather, save the token as the lesson describes and run bot.py.

Once handle_text is done, demo_check.py prints:

```text
Offline check: Recorded in the journal: kitchen, severity 1.
```

Checks: tests/test_lesson.py -> class LessonTests -> Run.
