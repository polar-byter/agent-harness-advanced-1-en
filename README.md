# Agent Harness Workshop. Stage 2: the model inside your application

A continuation of the [Agent Harness Workshop](https://github.com/polar-byter/agent-harness-workshop-en). In the main course the model ran separately - in OpenRouter, VseGPT or Ollama - and the program sent it messages. Here the model is loaded straight into a Python program and runs on the processor of an ordinary Windows laptop, with no network. With it we build real applications: a utility with a window that sorts an Excel journal, routing of customer requests to queues, a photo check for a return claim, a local web service, transcription of a voice message and a Telegram bot.

From the main course we take what is familiar: messages with the `system` and `user` roles, separate parsing of the answer, guardrails, checks on test examples, a person's approval before an important action, and the store with its returns policy. What is new: the model as part of the program, models of different kinds (language, a decision model in the Jev format, embeddings, vision, speech), answers strictly by a JSON schema and the design of an application the model is built into.

**[Start with the introduction](course/00-introduction.md)** / **[All lessons and starters](course/README.md)** / **[Results and cases](course/conclusion.md)**

## The route

| Lesson | What you get | Model |
|---|---|---|
| [1. The model inside the program](course/01-model-in-process.md) | A shared module and an `ask` function with answers by a schema | Qwen3-1.7B |
| [2. The cat's mischief journal](course/02-cat-journal.md) | A tkinter utility: Excel -> categories -> family bulletin | Qwen3-1.7B |
| [3. A model that makes decisions](course/03-decisions.md) | Routing requests to queues: questions in the Jev format from TypeSafe AI, probabilities and a threshold | Qwen3-1.7B |
| [4. A vision model checks the photo](course/04-vision.md) | Sorting return claims by their photos | Qwen3-VL-2B |
| [5. The model in a web service](course/05-movie-service.md) | Search by meaning in a Flask movie catalog | Qwen3-Embedding-0.6B |
| [6. Transcribing a voice message](course/06-speech.md) | A request card from a voice message | Whisper small + Qwen3-1.7B |
| [7. A Telegram bot](course/07-telegram-bot.md) | A bot with an allow list that adds to the journal | Qwen3-1.7B |

## How to learn here

You can read the lessons right on GitHub. For practice, download the lesson archive from the link in the lesson, extract it and open the lesson folder in PyCharm. You can also download the whole repository with **Code -> Download ZIP** and open the folder you need inside `exercises`.

In every starter everything written earlier already works, and the current function stops at `raise NotImplementedError(...)`. `demo_check.py` checks your function on a stand-in object without a model, `demo.py` runs the real model, and `tests/test_lesson.py` holds ready tests. [The source of all starters](exercises/README.md) can be viewed in the browser.

## What you need

Windows 10 or 11 x64, 8 GB of memory (16 is better), about 5 GB of disk space for the models, Python 3.14 and PyCharm. No graphics card is needed. The libraries install as ready packages, and the models are downloaded by `get_models.py` into a shared folder used by all lessons.

<details>
<summary>For course maintenance</summary>

[Editing rules](AGENTS.md) / [Build and checks](maintainer/README.md) / [Work log](maintainer/WORK_LOG.md)

</details>
