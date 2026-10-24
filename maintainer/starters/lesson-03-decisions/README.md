# A model that makes decisions

The model answers questions about a customer request with probabilities: which queue to send it to
and whether the customer is asking for their money back. The program makes the decision from these
probabilities. The questions follow the Jev format from TypeSafe AI, and the local Qwen3 answers them.

1. Open this folder in PyCharm with File -> Open and choose the shared course interpreter.
2. Install the dependencies: `python -m pip install --only-binary=:all: -r requirements.txt`.
3. Run get_models.py: if the language model from lesson 1 is already downloaded, nothing is loaded.
4. Complete ask_choice in decisions.py using TASK.md.
5. Run demo_check.py, then demo.py.
6. The same questions can go to a real decision model, pick one of the variants:
   - you have the OpenRouter connection from the main course: run demo_jev.py, Jev answers;
   - no such connection: install the library with the command at the top of frida_client.py and run
     demo_frida.py, the open FRIDA-Decisions answers on your CPU.

Once ask_choice is done, demo_check.py prints:

```text
Offline check: Charged twice for one order -> payment, confidence 0.97
```

Checks: tests/test_lesson.py -> class LessonTests -> Run.
