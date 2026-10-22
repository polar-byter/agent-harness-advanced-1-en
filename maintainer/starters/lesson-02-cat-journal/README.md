# The cat's mischief journal

A desktop utility on tkinter: it reads a journal from Excel, sorts the entries with a local model
and writes the result to a new sheet.

1. Open this folder in PyCharm with File -> Open and choose the shared course interpreter.
2. Install the dependencies: `python -m pip install --only-binary=:all: -r requirements.txt`.
3. If the model is not downloaded yet, run get_models.py.
4. Complete classify_entry in journal_ai.py using TASK.md.
5. Run demo_check.py, then demo.py. app.py opens the utility window.

Once classify_entry is done, demo_check.py prints:

```text
Offline check: Stole a meatball from the table while everyone was watching TV -> kitchen, severity 1
```

Checks: tests/test_lesson.py -> class LessonTests -> Run.
