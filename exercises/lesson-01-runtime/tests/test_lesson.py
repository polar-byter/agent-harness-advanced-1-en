import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo_check import DAYS, QUESTION, RULE, ExampleModel
from local_llm import ask


class LessonTests(unittest.TestCase):
    def test_plain_answer(self):
        model = ExampleModel('You can return an item within 14 days.')
        self.assertEqual(ask(model, RULE, QUESTION), 'You can return an item within 14 days.')
        settings = model.calls[0]
        self.assertTrue(settings['messages'][0]['content'].startswith(RULE))
        self.assertTrue(settings['messages'][0]['content'].endswith('/no_think'))
        self.assertEqual(settings['messages'][1], {'role': 'user', 'content': QUESTION})
        self.assertEqual(settings['max_tokens'], 256)

    def test_schema_answer(self):
        model = ExampleModel('{"days": 14}')
        self.assertEqual(ask(model, RULE, QUESTION, schema=DAYS, max_tokens=32), {'days': 14})
        self.assertEqual(model.calls[0]['response_format']['schema'], DAYS)

    def test_unfinished_generation(self):
        model = ExampleModel('You can return an item')
        model.create_chat_completion = lambda **settings: {
            'choices': [{'finish_reason': 'length', 'message': {'content': 'You can return an item'}}]}
        with self.assertRaises(ValueError):
            ask(model, RULE, QUESTION)


if __name__ == '__main__':
    unittest.main()
