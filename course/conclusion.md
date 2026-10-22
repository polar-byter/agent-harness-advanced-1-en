# What we built and where it is useful

In lesson 1 the model was loaded straight into our program for the first time and answered the familiar question about the return period. By the end of the course, on the same laptop, with no graphics card and no network, several applications run: a utility with a window sorts an Excel journal, routing distributes customer requests to queues, a check sorts return claims by their photos, a web service searches movies by meaning, transcription turns a voice message into a request card, and a Telegram bot adds to the family journal.

They all reach the models through one module, `local_llm.py`, and are built the same way: a ready application, one function where the model enters it, and a check of that function without a model on a stand-in object.

## What practice taught us

A small model on a processor copes with a narrow task if the task is stated precisely. With explanations for the categories Qwen3-1.7B sorted eleven of the twelve journal entries correctly, and with the names alone seven. After the explanations of "affection" and "damage" were adjusted, all twelve. The vision model was asked to name the object in the photo before comparing it with the order, which gives it a concrete thing to compare. The model itself did not change: only the description of the task changed.

A JSON schema is responsible only for the form of the answer. It guarantees that the category is one of five and that the `same_item` field is `true` or `false`. But the schema still forces the message "What's the weather tomorrow?" into one of the cat categories, and the vision model's comment may describe the object wrongly. So the program makes decisions on checkable fields, shows the free text to a person and measures accuracy on examples with a known answer.

The same goes for the model's confidence. In lesson 3 Qwen3 sent a question about gift cards to the payment queue with a probability of 1.00, and the threshold let this error through. What helped was the markup, where the error became visible, and a separate simple question - is the customer writing about a placed order - with the store's rule in code.

A model is a dependency of the application, just like a database. The movie catalog worked before the model and kept working with it, because the model came in through one class with a familiar method and one line at the composition point. In the same way the Telegram bot and the utility from lesson 2 use the same sorting function and are checked without Telegram and without a window.

The program still sets the boundaries. The bot lets only people from the allow list into the journal, the token is kept outside the project, and a staff member decides about refunds. These are the same guardrails and human approval as in the main course, only now around real applications.

## Labeling requests in-house

The Avito analysts from the introduction [labeled about 1,300 support requests](https://habr.com/ru/companies/avito/articles/950926/) (in Russian) with a local model and separately picked out, from two thousand conversations, those useful for a future knowledge base. The motive was the same as ours: the data must not be sent to external services.

After lesson 2 it is clear what such work consists of and who is responsible for what. An analyst writes the categories with explanations and collects a set of requests with correct labels. The program runs the model over all the records with an answer schema. Then the result is compared with the set, the explanations are adjusted and everything is run again. What matters to a manager here is that the labeling quality is measured on examples rather than taken on faith.

## Finding similar cases without losing a recurring problem

Anatoly, in [an article on searching ticket history](https://habr.com/ru/articles/945404/) (in Russian), describes a system for a closed network very similar to our lesson 5: tickets become embeddings, similar ones are found by cosine similarity, and the web service is written in Flask. The author also lists the difficulties: employees answered the same question differently, and old answers went out of date over time. So, he concludes, without a check of the knowledge base the reliability of answers is not guaranteed, and it is safer to rely on approved documentation.

This echoes the main course: the model relies on the source it was given. Embeddings find similar cases, but only whoever is responsible for the source can decide which answer is correct.

## Voice and photos as data

YooMoney [transcribes call-center calls](https://habr.com/ru/post/896096/) (in Russian) with Whisper and builds a dashboard of frequent user problems from them. The author of [a recognition comparison on 200 phone recordings](https://habr.com/ru/articles/1020632/) (in Russian) shows the price of a local solution: Whisper large-v3 got 14.2% of words wrong versus 8.1% for the cloud SpeechKit, and it did not mark unclear places but replaced them with plausible text. That is why in lesson 6 we show the operator the transcript with time marks next to the card: with them it is easy to listen to a doubtful place again.

At Wildberries [a vision model checks moderation flags](https://habr.com/ru/articles/992716) (in Russian): it receives a photo and a question and answers "yes" or "no", and it runs only on selected images to reduce false positives and take load off people. This is the same idea as in lesson 4: the model answers a closed question, and in doubtful cases the outcome stays with a person.

## A home bot as a first project

The bot [described by rocet](https://habr.com/ru/articles/1008248/) (in Russian) went from a simple chat partner to mini-games on local models. Its limitations match ours: the bot works while the computer is on, and the model does not always follow the prompt, so some problems have to be solved in code. Such a project is good for a first experience: the task is clear, the mistakes are harmless, and they show well where the program has to back up the model.

## Which task to take next

Choose a task where the data cannot or should not be sent outside and where you can check the correct answer yourself: labeling an export of requests, finding duplicates in a list of requirements, transcribing meeting recordings, sorting photos from a site. Start with copies of data you are allowed to use this way, and with twenty or thirty examples with a known answer.

From there the path is familiar: a model-loading module, one function with an answer schema, a check on a stand-in model, a run on the examples, adjusting the descriptions and running again. Change one thing at a time, so you can see what helped. If a small model falls short, that is a result too: you will know on which examples it fails and can reasonably ask for a bigger model or a graphics card.

Back to [the lessons and starters](README.md) or to the [conclusion of the main course](https://github.com/polar-byter/agent-harness-workshop-en/blob/main/course/conclusion.md).
