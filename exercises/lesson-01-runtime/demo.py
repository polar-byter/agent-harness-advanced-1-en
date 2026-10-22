from time import perf_counter

from demo_check import DAYS, QUESTION, RULE, check_exercise
from local_llm import ask, load_chat


def main():
    print(QUESTION)
    try:
        # First check the exercise without a model, then load the real one.
        check_exercise()
        with load_chat() as model:
            start = perf_counter()
            print('Model answer:', ask(model, RULE, QUESTION))
            print('Answer time, s:', round(perf_counter() - start, 1))
            data = ask(model, 'Find the return period in days in the policy clause.', QUESTION,
                       schema=DAYS, max_tokens=32)
            print('Answer by schema:', data, '- type:', type(data['days']).__name__)
    except (NotImplementedError, FileNotFoundError, ModuleNotFoundError, ValueError) as error:
        print(error)


if __name__ == '__main__':
    main()
