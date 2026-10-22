# Hints for lesson 7. A Telegram bot on a local model

> **Where we are.** The cat journal from lesson 2 gets a Telegram bot: family members send it entries, and it sorts them with the local model and writes them to the same Excel file. Today we write `handle_text`, which decides what the bot replies.
> **From the main course:** the program's access rule is written in code, not in a prompt; a separate check of logic without a network.
> **New:** the Telegram Bot API, long polling, a token outside the code, an allow list of users.
> `Telegram message -> bot.py -> allow list -> handle_text -> classify_entry -> Excel journal -> reply in the chat`

Current task: `bot_logic.py` -> `handle_text`. The full lesson: course/07-telegram-bot.md in the course repository.

## Your turn

Open `bot_logic.py`. `handle_text` receives the model, the journal path, the author's name and the message text. The checks for an empty and a too-long text are already there: a long text never reaches the model. Replace the line `raise NotImplementedError(...)` with the fragment below and fill in the two gaps:

```python
    entry = classify_entry(model, ...)
    append_entry(journal_path, author, text, extra=(entry['category'], entry['severity']))
    return f'Recorded in the journal: {entry["category"]}, severity {...}.'
```

1. Pass `text` to `classify_entry`. This is the same function from lesson 2; here it is already done.
2. In the reply after the word "severity" put `entry["severity"]` - with double quotes, because the whole f-string is in single quotes.

`append_entry` from `journal_io.py` adds a row to the end of the journal with today's date, the author and the text, and through `extra` the category and severity go into columns D and E. The utility from lesson 2 reads the first three columns, so it opens the extended journal without changes.

## Guess before running

What will the bot answer if a family member writes to it "What's the weather tomorrow?" by mistake? And what will a person not on the allow list see?

## Run it without Telegram

Open `demo_check.py` and choose **Run 'demo_check'**. The check works with a copy of the journal in a temporary folder and a stand-in model, so the real journal does not change. Once the function is done:

```text
Offline check: Recorded in the journal: kitchen, severity 1.
```

Now **Run 'demo'**. This is a conversation with the bot without Telegram: two entries from Emma and Dad and the `/summary` command, and the journal is a copy, `data/demo-journal.xlsx`. When the course was prepared:

```text
Emma: Grabbed a sausage off the table while I was pouring tea
Bot: Recorded in the journal: kitchen, severity 2.
Dad: Knocked my headphones off the shelf, an ear cushion broke off
Bot: Recorded in the journal: damage, severity 2.
Bot on /summary: Latest entries by category: {'kitchen': 1, 'damage': 1}
```

The bulletin from the model follows the count. Read it critically: in our run the model added details that are not in the entries, such as "a smudge of meat on the counter". The rule "add nothing of your own" does not fully hold for a small model, which is one more reason the bot records the category from the schema and shows the bulletin only as entertainment. `demo.py` calls the same functions as `bot.py`, so before meeting Telegram we already know the bot's logic works.

## Run it in Telegram

1. Open `bot.py` and choose **Run 'bot'**. The model loads, and Run shows `Bot started, allowed users: 0`.
2. In Telegram open your bot at the address you gave in BotFather and press **Start**. The bot replies with the help text.
3. Send `/id`. The bot sends your number.
4. Stop the bot with **Stop**, open `data/allowed_users.txt` and add the number on a new line. The list is read at startup, so run `bot.py` again.
5. Write a piece of mischief to the bot, for example "Stole a piece of cheese from my sandwich". While the model is thinking, the chat shows "typing...", then the reply with the category arrives.
6. Send `/summary` and get the bulletin. Open `data/journal.xlsx` in Excel - the new entries are at the end of the sheet. Close the file in Excel before the next entry: while it is open, Windows will not let the program overwrite it, and the bot will ask you to close the journal.

For the bot to add to the journal, the laptop must be on and `bot.py` running.

## Try to break it

**Write about something other than the cat.** Send "What's the weather tomorrow?". When the course was prepared, the model filed "What's the weather tomorrow?" under noise and "Remind me to buy milk" under affection: the schema allows only five categories, and the model has to pick one of them. To keep the bot from cluttering the journal, you can add a sixth category to `CATEGORIES`, for example "not about the cat", and not record such messages in `handle_text`. Try doing it yourself.

**Write from someone else's account.** Ask somebody to write to the bot. They get a refusal and the hint about `/id`, and the journal does not change.

**Switch the bot off.** Stop `bot.py`, send it a couple of messages and start it again. The bot handles them after the start: Telegram kept them all that time.
