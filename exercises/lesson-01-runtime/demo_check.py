from local_llm import ask

RULE = "Answer the customer's question from the policy clause. If the clause has no answer, say so."
QUESTION = ('Question: How many days do I have to return an item?\n'
            'Policy clause: Returns are accepted within 14 days.')
DAYS = {'type': 'object', 'properties': {'days': {'type': 'integer'}}, 'required': ['days']}


class ExampleModel:
    """A stand-in for the model: it remembers the call and returns the given text."""

    def __init__(self, content):
        self.content = content
        self.calls = []

    def create_chat_completion(self, **settings):
        self.calls.append(settings)
        return {'choices': [{'finish_reason': 'stop', 'message': {'content': self.content}}]}


def check_exercise():
    model = ExampleModel('<think>\n\n</think>\n\nYou can return an item within 14 days.')
    answer = ask(model, RULE, QUESTION)
    assert len(model.calls) == 1, 'Expected one call to the model'
    messages = model.calls[0]['messages']
    assert [item['role'] for item in messages] == ['system', 'user'], 'Two messages are needed: system and user'
    assert messages[1]['content'] == QUESTION, 'Pass text in the second message'
    assert 'response_format' not in model.calls[0], 'Without a schema no JSON restriction is needed'
    json_model = ExampleModel('{"days": 14}')
    assert ask(json_model, RULE, QUESTION, schema=DAYS) == {'days': 14}, 'With a schema, return a dictionary'
    return answer


def main():
    try:
        print('Offline check:', check_exercise())
    except NotImplementedError as error:
        print(error)


if __name__ == '__main__':
    main()
