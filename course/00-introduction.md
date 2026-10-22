# Stage 2: the model inside your application

BI analysts at Avito, Alexey Dubinets, Pavel Bespalov and Gleb Gladkov, describe in [an article on Habr](https://habr.com/ru/companies/avito/articles/950926/) (in Russian) how they labeled about 1,300 requests in their team's support chat with a local language model. Public cloud models did not fit the task: the requests can contain personal data and trade secrets, and these must not leave the company. They ran the model locally through LM Studio, and the labeling took about three and a half hours.

This is a direct continuation of the [main course, "Agent Harness Workshop"](https://github.com/polar-byter/agent-harness-workshop-en/blob/main/course/00-introduction.md). There the model ran separately from our program - in OpenRouter, VseGPT or Ollama - and the program sent it messages and parsed the reply. In stage 2 we take the next step: we load the model straight into a Python program, like an ordinary library, and build several real applications with it, from a desktop utility to a Telegram bot. Everything runs on an ordinary Windows laptop, on the processor, with no internet once the models are downloaded.

## What we take from the main course

The running example of the main course was an assistant that answers online store customers from a returns policy. We wrote `find_notes` and `read_notes`, assembled messages for the model in `build_messages`, sent them through `send_live` and parsed the answer. Then the model got tools, and `dispatch_tool` began letting through only permitted actions: such checks are called guardrails. The `run_agent` loop passed the tool result into the next request, the log recorded every step, test scenarios (evals) checked behavior after changes, and the coding agent applied a change only with a person's approval.

All of this will come in handy in stage 2. Messages with the `system` and `user` roles work the same way. Parsing the model's answer is again kept separate from calling it. The JSON schema we meet in lesson 1 works like a guardrail, only it acts earlier: the model physically cannot write a category that is not on the list. In the photo lesson a staff member still decides about refunds, and the Telegram bot lets only people from an allow list write to the journal. The store and its returns are still here too: customer requests, product photos and a customer's voice message come from the same store.

If you have not taken the main course, you can start here, but some explanations rely on it. In those places there is a link to the relevant lesson.

## What is new

A model inside the program behaves differently from a service over the network. The model file is loaded into our process's memory, and our program has to free that memory too. The data goes nowhere, so the question "may we send this outside" simply does not come up. On the other hand, speed, memory and the choice of model are now your concern: a small model on a processor makes more mistakes than a big cloud one, and in the lessons you will see these mistakes with your own eyes.

Besides the language model that writes text, we work with models of other kinds. Models of the System One class, such as Jev from TypeSafe AI, do not write answers: they choose an option and report its probability, and the program decides based on it. An embedding model turns text into a set of numbers that lets you find texts with a similar meaning. A vision model looks at a product photo. Whisper transcribes a voice message. We connect each of them the same way: a model file, a shared loading module and a function that passes the data to the model and takes the result back.

And most important, the applications are real. A utility with a window reads Excel, a local web service runs in the browser, a bot answers in Telegram. In each lesson the ready application already works, and you write the part where the model enters it.

## Why this matters to you

**An analyst** gets from stage 2 what is usually missing when setting a task with AI: an understanding of what a small local model does well and where it makes mistakes. In the journal lesson you will see how classification accuracy depends on the category descriptions, which an analyst writes, not a programmer. In the request-routing lesson you will see how a confidence threshold decides which requests the program routes itself and which go to people. When you propose labeling requests the way Avito did, you will already know which answer schema to set, how to check the result on test examples and how many examples to review by hand before trusting the labels.

**A manager or process owner** cares about control. A local model removes the question of where the data goes, but not the responsibility for the result. After the lessons you will know where such an application has its control points: a list of allowed answers, a person's check before a decision about money, a log showing what the model answered. That helps decide which tasks can be handed to a model completely and which only as a draft for a staff member.

**An administrator** finds a local model easy to understand in terms of access: it does not go online and cannot do anything beyond the program that calls it. So that program sets the boundaries. In the Telegram bot lesson the token is kept outside the code, and only users from an allow list can write to the journal. The model is a file of a specific version that you can check, pin and leave un-updated without your knowledge.

## Route

| Lesson | Application and model | What you write |
|---|---|---|
| [1. The model inside the program](01-model-in-process.md) | An answer from the returns policy, Qwen3 through llama-cpp-python | The `ask` function, shared by the whole course |
| [2. The cat's mischief journal](02-cat-journal.md) | A utility with a window: Excel -> categories -> bulletin | Classifying an entry with a JSON schema |
| [3. A model that makes decisions](03-decisions.md) | Routing customer requests to queues, questions in the Jev format on Qwen3 | Choosing an option with a probability |
| [4. A vision model checks the photo](04-vision.md) | A photo from a return claim, Qwen3-VL | Passing a picture to the model |
| [5. The model in a web service](05-movie-service.md) | A movie catalog on Flask, an embedding model | Search by meaning as a new service strategy |
| [6. Transcribing a voice message](06-speech.md) | A customer's voice message, Whisper | A transcript with time marks |
| [7. A Telegram bot](07-telegram-bot.md) | A bot for the cat journal | Handling a message |

At the end there is a [conclusion](conclusion.md) with published cases where such applications already work. A detailed list with the archives is on the page of [all lessons and starters](README.md).

## What you need

A laptop with 64-bit Windows 10 or 11, a recent processor and 8 GB of memory; with 16 GB things are noticeably more comfortable. When the course was prepared, the program with the largest model took about 2.3 GB of memory, but PyCharm and a browser are usually open alongside it. No graphics card is needed. You need about 5 GB of disk space for all the course models: their files sit in one shared folder and are downloaded once.

You need Python 3.14 from python.org and PyCharm, as in the main course. The library for running models installs as a ready package, so nothing has to be compiled. Lesson 1 explains in detail how to install it into an environment shared by all lessons.

## How the lessons work

Each lesson starts with a "Where we are" block: what we are building, what we take from the main course and what is new. Then come the situation and the data, then a prepared function with gaps and a hint for each. Before running, try to guess the result; after running, break something and see what happens.

Each lesson has its own starter archive. Everything written earlier already works in it, and the current function stops at the line `raise NotImplementedError(...)`. Next to it are `TASK.md` with hints, `demo_check.py`, which checks your function without a model on a stand-in object, and `demo.py`, which runs the real model. The diagrams in the lessons show which data goes where; you will get the real model answers yourself, and they may differ from the examples in the text.

Start: [lesson 1. The model inside the program](01-model-in-process.md).
