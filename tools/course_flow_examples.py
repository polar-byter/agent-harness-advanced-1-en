"""Concrete data for the lesson diagrams. These are teaching scenarios, not recordings of runs."""

STORIES = []


def transfer(action, source, before, destination, after, explanation, packet='data', summary=None):
    result = dict(action=action, source=source, before=before, destination=destination,
                  after=after, explanation=explanation, packet=packet)
    if summary:
        result['summary'] = summary
    return result


def story(name, title, *scenes):
    STORIES.append(dict(path='assets/' + name + '.gif', title=title, scenes=list(scenes)))


story('lesson-01-ask', 'How ask calls the model',
    transfer('demo.py calls ask', 'The call in demo.py',
             'ask(model, RULE, QUESTION,\n    schema=DAYS, max_tokens=32)',
             'Parameters of ask', 'instruction = "Find the return period ..."\ntext = "Question: How many days ..."\nschema = {"days": integer}',
             'The model is already loaded into the program memory by the with load_chat() block.', 'arguments',
             'The rule, the question with the clause and the schema land in the parameters of ask.'),
    transfer('ask builds the messages', 'Parameters of ask', 'instruction, text, schema',
             'messages and settings', '[system: rule + /no_think,\n user: question and clause]\nresponse_format: schema DAYS',
             'The schema becomes a grammar: the model can write only JSON of this shape.', 'messages'),
    transfer('The model answers inside the program', 'model.create_chat_completion', 'messages + settings\nno HTTP request',
             'response', '{"choices": [{"finish_reason": "stop",\n  "message": {"content": "{\\"days\\": 14}"}}]}',
             'This is an ordinary Python function call: the data never leaves the computer.', 'call'),
    transfer('ask returns a dictionary', 'clean_answer + json.loads', 'the string \'{"days": 14}\'',
             'The result in demo.py', "data = {'days': 14}\ntype(data['days']) -> int",
             'clean_answer checked finish_reason, and json.loads turned the string into a dictionary.', 'return'))

story('lesson-02-journal', 'An Excel journal becomes a review',
    transfer('Read the journal', 'data/journal.xlsx, sheet "Journal"', '2026-10-03 | Mom |\nStole a meatball from the table...',
             'The entries list', "[{'date': '2026-10-03', 'author': 'Mom',\n  'text': 'Stole a meatball...'}, ...]",
             'read_journal skips the header and rows without text. No model is involved yet.', 'read_journal'),
    transfer('Sort one entry', 'classify_entry(model, text)', 'text = "Stole a meatball..."\na rule with five categories',
             'The answer of ask with a schema', "{'category': 'kitchen', 'severity': 1}",
             'The enum in the schema allows only the five category names.', 'ask + schema'),
    transfer('Collect the results', 'process_journal', 'entry + category + severity\nfor each of the 12 entries',
             'results and the count', "{'noise': 3, 'hunting': 3, 'damage': 3,\n 'affection': 2, 'kitchen': 1}",
             'Entries are sorted one by one: that makes it easier to find where the model went wrong.', '12 entries'),
    transfer('Save to Excel', 'results + the bulletin from the model', 'categories and the bulletin text',
             'data/journal.xlsx', 'New sheet "Review":\nentries, categories, severity, bulletin',
             'save_results recreates the "Review" sheet; the original journal sheet does not change.', 'save_results'))

story('lesson-03-decisions', 'How a request reaches a queue',
    transfer('Build the question', 'R-101 and the queue question', '"I want my money back for the kettle,\n it won\'t switch on"\n6 options from questions.json',
             'Prompt text', 'Customer request: I want my money...\nQuestion: Which support queue...\n1. Return... 2. Complaint...',
             'The options are numbered: the model answers with one digit.', 'prompt'),
    transfer('The model scores the first token', 'model.create_completion', 'max_tokens=1\nlogits_processor=[remember]',
             'Scores of the number tokens', '"1": 31.2  "2": 39.9  "3": 28.4\n"4": 30.1  "5": 22.6  "6": 27.8',
             'remember keeps the scores of all 151,936 tokens; we need six of them.', 'scores'),
    transfer('Scores become probabilities', 'softmax in option_probabilities', '[31.2, 39.9, 28.4, 30.1, 22.6, 27.8]',
             'The answer of ask_choice', "{'choice': 'complaints', 'confidence': 1.00,\n 'probabilities': {'returns': 0.00,\n  'complaints': 1.00, ...}}",
             'The answer has the same shape as Jev\'s.', 'ask_choice'),
    transfer('The program decides', 'route(answers, threshold=0.9)', "choice = 'complaints'\nconfidence = 1.00",
             'Decision', "'complaints'\nWith confidence 0.74 it would be 'person'.",
             'Below the 0.9 threshold the model hesitates, and an operator would handle the request.', 'route'))

story('lesson-04-photo', 'A claim photo and the decision on it',
    transfer('Prepare the picture', 'data/photos/phone.jpg', 'JPEG file bytes',
             'A data URI string', '"data:image/jpeg;base64,/9j/4AAQ..."',
             'The picture travels inside the message as base64 text; the file is not uploaded anywhere.', 'base64'),
    transfer('Build the message', 'Claim A-1043', "item = 'smartphone'\nphoto = 'phone.jpg'",
             'The user message', '[picture: data:image/jpeg...,\n text: "Ordered item: smartphone"]',
             'The message content is a list of two parts: the picture and the text.', 'messages'),
    transfer('The vision model answers by the schema', 'Qwen3-VL: projector + language part', 'picture -> vectors\ntext -> tokens',
             'The answer of check_photo', "{'item': 'smartphone', 'same_item': True,\n 'damage_visible': True, 'comment': ...}",
             'First the model names the object, then compares it with the order.', 'JSON'),
    transfer('The program picks a route', 'route_return(check)', 'same_item = True\ndamage_visible = True',
             'Decision', '"to staff: damage is visible in the photo"',
             'The decision is built from yes/no fields. A staff member refunds the money.', 'route'))

story('lesson-05-service', 'Search by meaning inside a web service',
    transfer('The browser sends a request', 'Address in the browser', '/?q=hockey movie',
             'web.py', "query = 'hockey movie'\nservice.find(query)",
             'The web layer reads the parameter and passes it to the service.', 'HTTP'),
    transfer('The service takes the movies and the strategy', 'CatalogService.find', 'repository.list_all() -> 10 movies\nself.search -> SemanticSearch',
             'SemanticSearch.find', "query + 10 movies, top = 3",
             'The service does not know which search run.py gave it.', 'find'),
    transfer('The strategy compares vectors', 'SemanticSearch', 'vector(TASK + query)\nmovie_vector(movie) from self.vectors',
             'Pairs (closeness, movie)', '(0.54, Miracle)\n(0.38, The Snowman) ...',
             'The movie vectors are computed once and kept in the self.vectors dictionary.', 'cosine'),
    transfer('A page with the list', 'The three best movies', "['Miracle', ...]",
             'Browser', 'index.html: cards of the found movies',
             '/api/search returns the same result as JSON.', 'page'))

story('lesson-06-speech', 'From a voice message to a request card',
    transfer('Read the sound', 'data/call.wav', '20.9 seconds, 16,000 Hz, mono, 16 bits',
             'audio', '334,640 numbers from -1 to 1\n[0.0, 0.0012, -0.0031, ...]',
             'read_wav checks the format and divides the samples by 32768.', 'read_wav'),
    transfer('Whisper recognizes the speech', 'model.transcribe(audio, language="en")', '334,640 numbers',
             'Segments', "Segment(t0=744, t1=1164,\n  text=' Two weeks ago...')",
             'Segment times are in hundredths of a second.', 'Whisper'),
    transfer('Build lines with time marks', 'A segment', 't0 = 744 -> 7 seconds\ntext.strip()',
             'lines', "'[00:07] Two weeks ago I bought...'",
             'With the time mark an operator quickly finds the place in the recording.', 'transcribe'),
    transfer('Qwen3 fills in the card', 'Transcript lines', 'the transcript text\nCALL_RULE + CALL_SCHEMA',
             'Request card', "{'name': 'Olivia Parker', 'order': '4512',\n 'wish': 'refund',\n 'callback': 'after six in the evening'}",
             'The second model gets only the text: the first model\'s errors pass on to it.', 'ask + schema'))

story('lesson-07-bot', "A message's path through the bot",
    transfer('Telegram hands over a message', 'Telegram servers', 'Emma: "Grabbed a sausage off the table"',
             'bot.py, long polling', 'message.from_user.id = 5012...\nmessage.text = "Grabbed a sausage..."',
             'The program itself asks Telegram for new messages.', 'getUpdates'),
    transfer('Check the allow list', 'message.from_user.id', '5012...',
             'data/allowed_users.txt', 'id in the list -> handle_text\nnot in the list -> a polite refusal',
             'The access rule is written in code; a chat message does not change it.', 'id'),
    transfer('Sort and record', 'handle_text', 'classify_entry(model, text)',
             'data/journal.xlsx', "new row: date, Emma, text,\n'kitchen', 2",
             'The same sorting as the utility from lesson 2, and the same journal.', 'append_entry'),
    transfer('Reply in the chat', 'The reply string', '"Recorded in the journal: kitchen, severity 2."',
             'The Telegram chat', "A reply to Emma's message",
             'bot.reply_to sends the reply through the Bot API.', 'reply_to'))
