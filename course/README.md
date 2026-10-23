# All lessons and starters

Stage 2 of the [main course, "Agent Harness Workshop"](https://github.com/polar-byter/agent-harness-workshop-en/blob/main/course/README.md). Start with the [introduction](00-introduction.md): it explains what we take from the main course and what is new.

It is best to take the lessons in order: the first creates the shared Python environment and downloads the language model, the second and seventh work with one journal, and the third continues the answer-schema idea from the second. But every starter is self-contained: everything written in earlier lessons is already done in it.

| Lesson | Starter | Models | New libraries |
|---|---|---|---|
| [1. The model inside the program](01-model-in-process.md) | [lesson-01-runtime](../downloads/lesson-01-runtime.zip?raw=true) | Qwen3-1.7B, 1.8 GB | llama-cpp-python |
| [2. The cat's mischief journal](02-cat-journal.md) | [lesson-02-cat-journal](../downloads/lesson-02-cat-journal.zip?raw=true) | Qwen3-1.7B | openpyxl |
| [3. A model that makes decisions](03-decisions.md) | [lesson-03-decisions](../downloads/lesson-03-decisions.zip?raw=true) | Qwen3-1.7B | - |
| [4. A vision model checks the photo](04-vision.md) | [lesson-04-vision](../downloads/lesson-04-vision.zip?raw=true) | Qwen3-VL-2B, 1.6 GB | - |
| [5. The model in a web service](05-movie-service.md) | [lesson-05-movie-service](../downloads/lesson-05-movie-service.zip?raw=true) | Qwen3-Embedding-0.6B, 640 MB | Flask |
| [6. Transcribing a voice message](06-speech.md) | [lesson-06-speech](../downloads/lesson-06-speech.zip?raw=true) | Whisper small, 490 MB; Qwen3-1.7B | pywhispercpp |
| [7. A Telegram bot](07-telegram-bot.md) | [lesson-07-telegram-bot](../downloads/lesson-07-telegram-bot.zip?raw=true) | Qwen3-1.7B | pyTelegramBotAPI |

Results and published cases are in the [conclusion](conclusion.md).

## How to work with a starter

Download the lesson archive, extract it with **Extract All** and open the lesson folder in PyCharm with **File -> Open**. Choose the shared course environment `C:\Users\Name\agent-venv` (lesson 1 explains why it is needed, how to create it and when you can do without it) and install the dependencies with the command from the lesson. The models live in the shared folder `C:\Users\Name\agent-models`, and `get_models.py` in each starter downloads only the missing ones.

Every starter has:

- `TASK.md` - hints for the current task, assembled from the lesson text;
- `local_llm.py` - the shared model-loading module, the same in every lesson from the second on;
- `demo_check.py` - a check of your function on a stand-in object instead of the model; works without downloaded models;
- `demo.py` - a run with the real model;
- `tests/test_lesson.py` - ready tests: open the file and run `class LessonTests`.

Until you complete the function, `demo_check.py` and `demo.py` print a `Complete ...` hint, and the tests fail, as expected.
