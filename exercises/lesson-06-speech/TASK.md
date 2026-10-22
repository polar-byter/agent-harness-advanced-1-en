# Hints for lesson 6. Transcribing a voice message

> **Where we are.** A customer left a voice message. Whisper turns it into text with time marks, and the language model fills in a request card from the text. Today we write `transcribe`, which builds the lines of the transcript.
> **From the main course:** checking a model's answer against the source; the source is now a sound recording.
> **New:** a speech recognition model, sound as a sequence of numbers, a chain of two models.
> `call.wav -> read_wav -> numbers -> [transcribe: Whisper] -> lines with time -> call_card: Qwen3 + schema -> card`

Current task: `speech.py` -> `transcribe`. The full lesson: course/06-speech.md in the course repository.

## Your turn

`transcribe` receives the loaded Whisper model and the sound as numbers and has to return lines like `[00:07] Two weeks ago...`. The time mark is for the operator: with it they can quickly find the place in the recording and listen again. Replace the line `raise NotImplementedError(...)` with the fragment below and fill in the three gaps:

```python
    segments = model.transcribe(..., language='en')
    lines = []
    for segment in segments:
        seconds = ...
        lines.append(f'[{seconds // 60:02}:{seconds % 60:02}] {...}')
    return lines
```

1. Pass `audio` to `model.transcribe`.
2. Store `segment.t0 // 100` in `seconds`: integer division turns hundredths into whole seconds, so 744 becomes 7.
3. Put `segment.text.strip()` in the curly braces at the end of the line: `strip` removes the space at the start of the text.

`seconds // 60` gives whole minutes, `seconds % 60` the remaining seconds. `:02` inside the f-string pads the number with a zero to two digits, so 7 seconds become `00:07`. The `language='en'` parameter tells Whisper the language of the speech; we will see below what happens with the wrong one.

## Guess before running

The customer says the order number in words: "four five one two". How will Whisper write it in the transcript? And how will the language model fill in the `wish` field of the card, when the schema allows only "refund", "exchange", "repair", "advice" and "other" for it?

## Run it

Open `demo_check.py` and choose **Run 'demo_check'**. The stand-in model returns two ready segments, and the check looks at the time marks and the language. Once the function is done:

```text
Offline check: [00:07] Two weeks ago I bought an electric kettle from you,
```

Now **Run 'demo'**. First Whisper loads and the transcript appears, then Qwen3 loads and fills in the card. When the course was prepared:

```text
Recording length: 20.9 s
Transcribed in 2.3 s:
[00:00] Hello. My name is Olivia Parker, order number 4512.
[00:06] Two weeks ago I bought an electric kettle from you, and yesterday it stopped switching on.
[00:12] I would like my money back.
[00:15] I still have the receipt.
[00:17] Please call me back after six in the evening.
Request card: {'name': 'Olivia Parker', 'order': '4512', 'problem': 'electric kettle stopped switching on', 'wish': 'refund', 'callback': 'after six in the evening'}
```

The ready function `call_card` builds the card: it passes the transcript lines to `ask` with the rule `CALL_RULE` and the schema `CALL_SCHEMA`. The models are loaded one after another in separate `with` blocks, so only one of them is in memory at a time.

## Try to break it

**Name the wrong language.** In the `model.transcribe` call replace `language='en'` with `language='de'` and run `demo.py`. When the course was prepared, Whisper started in German, "Hallo. Mein Name ist Olivia Parker, Order #4512", and went on in English. With `language='ru'` it translated the whole message into Russian and lost the meaning on the way: "I still have the receipt" turned into "I still can't". The language model would fill in the card from such a text without noticing anything. Put `language='en'` back.

**Simplify the card rule.** In `CALL_RULE` delete the sentence that explains the `name`, `order`, `problem` and `callback` fields. When the course was prepared, without it the card was still filled in, but the `callback` field lost a word: "six in the evening" or "6pm" instead of "after six in the evening". For the operator that is a different instruction. Explaining the fields works the same way as explaining the categories in lesson 2. Put the sentence back.

**Record your own message.** The Windows Sound Recorder app saves files as m4a, and `read_wav` answers with the error `A WAV file is needed: 16,000 Hz, one channel, 16 bits`. If you have ffmpeg installed, convert the recording with the command below and point `demo.py` to the new file:

```powershell
ffmpeg -i recording.m4a -ar 16000 -ac 1 data\my.wav
```
