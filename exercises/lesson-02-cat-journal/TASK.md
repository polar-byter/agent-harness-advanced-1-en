# Hints for lesson 2. The cat's mischief journal

> **Where we are.** The first application with a window: a utility reads a journal from Excel, the model sorts the entries into categories and writes a bulletin. Today we write `classify_entry`, which sorts one entry.
> **From the main course:** a log as a way to reconstruct later what happened; checking on a set of test examples.
> **New:** a tkinter window, reading and writing Excel with openpyxl, classification with a list of allowed categories in a JSON schema.
> `Excel -> read_journal -> [classify_entry -> ask with a schema] -> categories -> bulletin -> "Review" sheet`

Current task: `journal_ai.py` -> `classify_entry`. The full lesson: course/02-cat-journal.md in the course repository.

## Your turn

`classify_entry` already checks for an empty entry. Replace the line `raise NotImplementedError(...)` with the fragment below and fill in the two gaps:

```python
    schema = {
        'type': 'object',
        'properties': {
            'category': {'type': 'string', 'enum': ...},
            'severity': {'type': 'integer', 'enum': [1, 2, 3]},
        },
        'required': ['category', 'severity'],
    }
    answer = ask(model, CLASSIFY_RULE, ..., schema=schema, max_tokens=64)
    return {'category': answer['category'], 'severity': answer['severity']}
```

1. In the category's `'enum':` put `list(CATEGORIES)`. A list made from a dictionary gives its keys: `['kitchen', 'damage', 'noise', 'affection', 'hunting']`.
2. Pass `text`, the text of the entry, as the third argument of `ask`.

The word `enum` in a schema means "one of the listed values". The model cannot write the category "food" or "mess", however much it wants to: only our five strings are allowed when tokens are chosen. The same goes for severity: only 1, 2 or 3. The `max_tokens=64` limit is more than enough for a short JSON like `{"category": "kitchen", "severity": 1}`. `ask` from lesson 1 returns it already as a dictionary, and we take the two fields we need from it.

## Guess before running

Reread the twelve journal entries. How many of them will the model sort the way you would? Which two or three entries seem debatable to you?

## Run it

Open `demo_check.py` and choose **Run 'demo_check'**. The stand-in model here answers by a keyword, and the check looks at whether you passed the entry text and the list of categories in the schema to the model. Once the function is done:

```text
Offline check: Stole a meatball from the table while everyone was watching TV -> kitchen, severity 1
```

Now **Run 'demo'**. The program loads the model and sorts all the entries. This is what one of the runs looked like when the course was prepared:

```text
  kitchen | 3 | Stole a meatball from the table while everyone was watching TV
    noise | 3 | Yowled outside the bedroom door at three in the morning
affection | 1 | Fell asleep on my lap and purred for a whole hour
  hunting | 1 | Caught a fly and left it in Dad's slipper
   damage | 3 | Clawed the new living room curtain to shreds
   ...
   damage | 1 | Slept on the freshly ironed shirts
   ...
affection | 1 | Met me at the door and rubbed against my legs
```

Below the table are the count by category and the family bulletin. The same model writes the bulletin as plain text, without a schema, following the rule `SUMMARY_RULE`.

Finally, open `app.py` and choose **Run 'app'**. A window appears. Click **Open journal**, choose `data/journal.xlsx`, then **Sort entries**. Entry numbers run through the status line, then the table fills with categories and the bulletin appears at the bottom. **Save to Excel** adds a "Review" sheet to the file. Close the file in Excel before saving, or Windows will not let the program overwrite it.

## Try to break it

**Remove the explanations.** In `CLASSIFY_RULE` replace the line with the list of categories with `', '.join(CATEGORIES)`, so the model sees only the names. Run `demo.py` and count the errors. Put it back.

**Remove the list from the schema.** Delete `'enum': list(CATEGORIES)` from the category and run `demo.py`. When the course was prepared, the model kept to the names from the rule even without the list, but now that rests only on its behavior. Change the rule or take another model, and next to "kitchen" the count may show "food", which nothing downstream expects. With the list in the schema an invalid name cannot appear at all, so put `enum` back.

**Add an empty row.** Insert a row in Excel with only the date filled in, save and run `demo.py`. The entry does not get sorted: `read_journal` skips rows without text.
