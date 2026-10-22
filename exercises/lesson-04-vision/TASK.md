# Hints for lesson 4. A vision model checks the photo

> **Where we are.** A return claim comes with a photo of the item. The vision model says what is in the photo, whether it is the ordered item and whether damage is visible, and the program decides where to send the claim. Today we write `check_photo`, which passes the picture to the model.
> **From the main course:** a person's approval before an important action; the program, not the model, decides.
> **New:** a vision model from two files, a message made of a picture and text, a schema with yes/no fields.
> `claim + photo -> [check_photo: picture + item name -> vision model] -> {item, same_item, damage_visible} -> route_return -> staff`

Current task: `photo_check.py` -> `check_photo`. The full lesson: course/04-vision.md in the course repository.

## Your turn

Replace the line `raise NotImplementedError(...)` in `check_photo` with the fragment below and fill in the two gaps:

```python
    messages = [
        {'role': 'system', 'content': PHOTO_RULE},
        {'role': 'user', 'content': [
            {'type': 'image_url', 'image_url': {'url': image_to_data_uri(...)}},
            {'type': 'text', 'text': 'Ordered item: ' + ...},
        ]},
    ]
    response = model.create_chat_completion(
        messages=messages, max_tokens=200, temperature=0.2,
        response_format={'type': 'json_object', 'schema': PHOTO_SCHEMA},
    )
    return json.loads(clean_answer(response))
```

1. Pass `photo`, the path to the photo file, to `image_to_data_uri`.
2. After "Ordered item: " add `ordered_item`, the name of the item from the claim.

Here we call the model directly, without `ask`: `ask` from lesson 1 builds the `user` message from a string, and we need a list of a picture and text. Parsing the answer is the same - `clean_answer` and `json.loads`. The low `temperature=0.2` reduces the randomness of token choice: for a check we need a stable answer, not varied wording.

## Guess before running

Look at the five claims in `data/returns.json` and the photos in `data/photos`. Where will `route_return` send each claim? For which of them can a photo not confirm the reason for the return at all?

## Run it

Open `demo_check.py` and choose **Run 'demo_check'**. The stand-in model always answers that the photo shows a broken smartphone. The check looks at whether the message has the picture first, as `data:image/jpeg;base64,...`, then the item name. Once the function is done:

```text
Offline check: to staff: damage is visible in the photo
```

Now **Run 'demo'**. Loading the two files takes a few seconds, then for each claim the model's answer and the decision appear. This is what a run looked like when the course was prepared, with the comments shortened:

```text
A-1042: electric kettle, reason "does not switch on", photo kettle.jpg
  Model: {'item': 'electric kettle', 'same_item': True, 'damage_visible': False, ...}
  Decision: to staff: no damage visible in the photo, the item needs checking (10 s)
A-1044: sneakers, reason "wrong size", photo mug.jpg
  Model: {'item': 'mug', 'same_item': False, 'damage_visible': False,
          'comment': 'The photo shows a mug with steam, not sneakers.'}
  Decision: ask for another photo: the picture does not show the ordered item (9 s)
A-1046: electric kettle, reason "arrived broken", photo phone.jpg
  Model: {'item': 'phone', 'same_item': False, 'damage_visible': True,
          'comment': 'The phone has a cracked screen.'}
  Decision: ask for another photo: the picture does not show the ordered item (7 s)
```

All five decisions were correct. Note how the decision is made: `route_return` looks only at the `same_item` and `damage_visible` fields, and a person reads the comment. In A-1046 the comment is accurate, but a small model's free text can also be wrong; it is a hint for the employee, and decisions are not built on it.

Claim A-1042 shows the limit of the method: the kettle "does not switch on", and that can never be seen in a photo. The model answered that no damage is visible, and the claim went to an item check.

## Try to break it

**Remove the item field.** In `PHOTO_SCHEMA` delete the line with `'item'` and remove `'item'` from the `required` list, and in `PHOTO_RULE` replace everything before the words "In comment" with: "You help check product photos for return claims. Compare the object in the photo with the ordered item and say whether damage is visible: cracks, chips, broken glass, dents." Run `demo.py` and look at claim A-1046. When the course was prepared, the English version answered correctly even without this field, in two runs out of two, so here the field works as insurance rather than a fix. Watch whether your run differs. The model fills the fields in order, and when it names the object first, the comparison with the order tends to be more accurate. Put the rule and the `item` field back in first place.

**Remove the length limit.** Delete `'maxLength': 200` from the comment, and replace the last sentence of the rule with "Answer in English.". Without a length limit the model may write a comment until it hits the 200-token limit, and then `clean_answer` reports `Generation did not finish`. See how the model behaves for you, and put the limit back.

**Slip in your own photo.** Take a photo of any object at home, save it as JPEG in `data/photos` and add a claim to `returns.json`. Check whether the model copes with your lighting and background.
