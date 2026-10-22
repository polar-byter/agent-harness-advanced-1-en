# Hints for lesson 1. The model inside the program

> **Where we are.** We are building a shared module through which every lesson of the course will reach the local model. Today we write its `ask` function.
> **From the main course:** two messages with the `system` and `user` roles from `build_messages`, answer parsing from `extract_answer`, the optional lesson on running a model from Python.
> **New:** the model lives in our program's memory, one loading module for the whole course, an answer strictly by a JSON schema.
> `question -> ask -> [messages -> model in program memory] -> text or dictionary`

Current task: `local_llm.py` -> `ask`. The full lesson: course/01-model-in-process.md in the course repository.

## Your turn

`ask` receives the loaded model `model`, the rule `instruction`, the data `text` and, if needed, the schema `schema`. The start is ready: the `settings` dictionary holds the token sampling settings from `SAMPLING` and the length limit, and `response_format` is added when a schema is passed. Replace the line `raise NotImplementedError(...)` with the fragment below and fill in the two gaps:

```python
    messages = [
        {'role': 'system', 'content': instruction + NO_THINK},
        {'role': 'user', 'content': ...},
    ]
    response = model.create_chat_completion(messages=..., **settings)
    answer = clean_answer(response)
    if schema is not None:
        return json.loads(answer)
    return answer
```

1. In the second message put `text`: the customer's question together with the policy clause.
2. Pass the `messages` list built just above to `messages=`.

The messages are built the same way as in `build_messages` of the main course: the rule in the `system` role, the data in the `user` role. `NO_THINK` is added to the rule - the Qwen3 command `/no_think`, so the model answers straight away without long reasoning. The two asterisks in `**settings` unpack the dictionary into named arguments: `max_tokens=256`, `temperature=0.7` and the rest. If a schema was passed, `json.loads` turns the string `'{"days": 14}'` into the dictionary `{'days': 14}`, and the function returns a dictionary; otherwise it returns a string.

The whole fragment sits inside the function with a four-space indent. The lines of the `messages` list are indented four more, and the final `return answer` is at the same level as `if`.

## Guess before running

`demo.py` asks the model the same question twice. The first time without a schema, the second time with the `DAYS` schema. What will the `type:` line print after the second answer: `str` or `int`?

## Run it

First open `demo_check.py` and choose **Run 'demo_check'**. Instead of the model, a stand-in object `ExampleModel` answers here: it remembers which messages it was given and returns a prepared text. So the check works without a model and even without the library installed. Once `ask` is done, Run shows:

```text
Offline check: You can return an item within 14 days.
```

If you see `Complete ask...`, the stub is still in place. A message like `Pass text in the second message` tells you which gap is filled in wrong.

Now open `demo.py` and choose **Run 'demo'**. You will see `Loading Qwen3-1.7B-Q8_0.gguf...`, then the model's answer, the answer time and the answer by the schema:

```text
Model answer: You have 14 days to return an item.
Answer time, s: 1.1
Answer by schema: {'days': 14} - type: int
```

The words of the first answer will be different for you, and the time depends on the computer. The second answer is a dictionary with a number: the `"integer"` schema set the type `int`.

## Try to break it

**Change the source.** In `demo_check.py` find `QUESTION` and replace "14 days" with "30 days". Run `demo.py`: both answers should say 30. If the model keeps writing 14, it is not answering from the supplied clause, and that is a reason to compare the answer with the source, as we did in the main course. Put 14 back.

**Cut the limit.** In `demo.py`, add the argument `max_tokens=5` to the first `ask` call. The model will not finish the sentence, `finish_reason` will be `'length'`, and instead of a fragment `clean_answer` raises the error `Generation did not finish`. This is how the program tells a finished answer from a cut-off one. Remove the argument.

**Change the type in the schema.** In `DAYS` replace `'integer'` with `'string'`. Now the second answer is a string of type `str`. When the course was prepared, the model wrote `{"days": "Do you have to return an item within 14 days?"}` in one run, and in two other runs it kept writing a sentence inside the string until it hit the 32-token limit, so `clean_answer` raised `Generation did not finish`. The schema allowed any string, and the model filled it with words instead of a number. With the `'integer'` type such an answer is impossible. Put `'integer'` back.
