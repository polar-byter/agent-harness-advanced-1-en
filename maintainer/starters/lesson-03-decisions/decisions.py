"""The model answers questions about a request with probabilities, and the program makes the decision.

Questions and answers follow the Jev format from TypeSafe AI: the types choice, score and noul.
The local Qwen3 answers: option probabilities come from its scores for the first token of the answer.
"""
import json
import math
from pathlib import Path

SYSTEM = 'You assess requests from online store customers. Answer with the option number only.'
# This is how the Qwen3 template marks up messages. The empty <think> block at the end asks for an
# immediate answer, so the first token of the answer is the option number.
PROMPT = ('<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n'
          '<|im_start|>assistant\n<think>\n\n</think>\n\n')


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def option_probabilities(model, state: str, instructions: str, options: list[str]) -> list[float]:
    """Probability of each option: the model scores the option numbers as the first token of the answer."""
    if not 2 <= len(options) <= 9:
        raise ValueError('There must be 2 to 9 options: the option number is a single digit')
    labels = [str(number) for number in range(1, len(options) + 1)]
    lines = '\n'.join(f'{label}. {text}' for label, text in zip(labels, options))
    user = f'Customer request: {state}\n\nQuestion: {instructions}\n{lines}\n\nAnswer (one number):'
    seen = []

    def remember(tokens, scores):
        seen.append(scores.copy())  # scores of every vocabulary token before the first token is chosen
        return scores

    model.create_completion(PROMPT.format(system=SYSTEM, user=user), max_tokens=1, temperature=0,
                            logits_processor=[remember])
    logits = [float(seen[0][model.tokenize(label.encode('utf-8'), add_bos=False)[0]]) for label in labels]
    # Softmax: the scores become probabilities that add up to 1.
    top = max(logits)
    weights = [math.exp(value - top) for value in logits]
    return [weight / sum(weights) for weight in weights]


def ask_choice(model, state: str, question: dict) -> dict:
    """A choice question: which option from criteria fits. The answer has the same shape as Jev's."""
    names = list(question['criteria'])
    values = option_probabilities(model, state, question['instructions'], list(question['criteria'].values()))
    # Collect the probabilities by option name, pick the most probable one and return the answer.
    raise NotImplementedError('Complete ask_choice in decisions.py using the lesson 3 hints')


def ask_score(model, state: str, question: dict) -> dict:
    """A score question: a level on the criteria scale. score is the mean level weighted by probability."""
    values = option_probabilities(model, state, question['instructions'], question['criteria'])
    return {'type': 'score', 'score': sum(level * value for level, value in enumerate(values)),
            'probabilities': {str(level): value for level, value in enumerate(values)}}


def ask_noul(model, state: str, question: dict) -> dict:
    """A noul question: yes or no. noul is the probability of "yes"."""
    # A small model leans towards the first option, so "No" goes first.
    _, yes = option_probabilities(model, state, question['instructions'], ['No', 'Yes'])
    return {'type': 'noul', 'noul': yes}


ASK = {'choice': ask_choice, 'score': ask_score, 'noul': ask_noul}


def decide(model, state: str, questions: dict) -> dict:
    """Each question is asked separately, as in Jev: the answer to one does not affect another."""
    answers = {}
    for name, question in questions.items():
        if question['type'] not in ASK:
            raise ValueError('Unknown question type: ' + question['type'])
        answers[name] = ASK[question['type']](model, state, question)
    return answers


def route(answers: dict, threshold: float = 0.9) -> str:
    """The program decides: a confident choice goes to its queue, everything else to a person."""
    queue = answers['queue']
    if queue['choice'] == 'other' or queue['confidence'] < threshold:
        return 'person'
    return queue['choice']


def describe(request: dict, answers: dict, threshold: float = 0.9) -> str:
    """A report line: the program's decision, the model's answer and the yes/no questions answered "yes"."""
    queue = answers['queue']
    guess = f'{queue["choice"]} {queue["confidence"]:.2f}'
    marks = ' '.join(name for name, answer in answers.items() if answer['type'] == 'noul' and answer['noul'] >= 0.5)
    return f'{request["id"]} {route(answers, threshold):10} {guess:15} {marks:7} {request["text"]}'


def compare_with_markup(results: list, threshold: float = 0.9) -> dict:
    """Compare the program's decisions with the markup in each request's queue field."""
    report = {'auto': 0, 'correct': 0, 'manual': [], 'wrong': []}
    for request, answers in results:
        decision = route(answers, threshold)
        if decision == 'person':
            report['manual'].append(request['id'])
            continue
        report['auto'] += 1
        if decision == request['queue']:
            report['correct'] += 1
        else:
            report['wrong'].append((request['id'], decision, answers['queue']['confidence'], request['queue']))
    return report


def print_report(results: list, threshold: float = 0.9) -> None:
    """The same report for any source of answers: Qwen3, Jev or FRIDA."""
    for request, answers in results:
        print(describe(request, answers, threshold))
    report = compare_with_markup(results, threshold)
    print(f'Threshold {threshold}. Routed by the program: {report["auto"]}, '
          f'matching the markup: {report["correct"]}. To a person: {len(report["manual"])}.')
    for number, decision, confidence, expected in report['wrong']:
        print(f'  Mismatch: {number} -> {decision} with confidence {confidence:.2f}, markup says {expected}')
