from pathlib import Path

from decisions import ask_choice, read_json

ROOT = Path(__file__).resolve().parent
STATE = 'Charged twice for one order'


class ExampleModel:
    """A stand-in for the model: the option whose words appear in the request gets a high score."""
    WORDS = {'Return': ('send back', 'exchange', 'return'),
             'Complaint': ('broke', 'broken', "won't switch on", 'missing', 'wrong'),
             'Delivery': ('courier', 'delivery', 'arrived', 'where is my order'),
             'Payment': ('charged', 'payment'), 'Account': ('account',), 'Yes': ('broke', 'broken')}

    def __init__(self):
        self.prompts = []

    def tokenize(self, text, add_bos=True):
        return [int(text.decode('utf-8'))]  # every option number has its own "token"

    def create_completion(self, prompt, max_tokens, temperature, logits_processor):
        self.prompts.append(prompt)
        state = prompt.split('Customer request: ')[1].split('\n')[0].casefold()
        scores = [0.0] * 10
        for line in prompt.splitlines():
            number, dot, option = line.partition('. ')
            if dot and number.isdigit():
                words = self.WORDS.get(option.split(':')[0].split()[0], ())
                scores[int(number)] = 5.0 * sum(word in state for word in words)
        for processor in logits_processor:
            scores = processor([], scores)
        return {'choices': [{'text': '1'}]}


def check_exercise():
    model = ExampleModel()
    question = read_json(ROOT / 'data' / 'questions.json')['queue']
    answer = ask_choice(model, STATE, question)
    assert isinstance(answer, dict) and answer.get('type') == 'choice', 'Return a dictionary with "type": "choice"'
    probabilities = answer.get('probabilities')
    assert isinstance(probabilities, dict) and list(probabilities) == list(question['criteria']), \
        'probabilities holds the option names from criteria in the same order'
    assert answer.get('choice') == max(probabilities, key=probabilities.get), 'choice holds the most probable option'
    assert answer.get('confidence') == probabilities[answer['choice']], 'confidence holds the probability of the chosen option'
    return f'{STATE} -> {answer["choice"]}, confidence {answer["confidence"]:.2f}'


def main():
    try:
        print('Offline check:', check_exercise())
    except NotImplementedError as error:
        print(error)


if __name__ == '__main__':
    main()
