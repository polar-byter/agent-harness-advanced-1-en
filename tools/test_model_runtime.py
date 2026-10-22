"""Tests of the shared local_llm.py module on stand-in objects: no model libraries and no network."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'model_runtime'))
import local_llm


class FakeModel:
    def __init__(self, content, finish='stop'):
        self.content, self.finish, self.calls = content, finish, []

    def create_chat_completion(self, **settings):
        self.calls.append(settings)
        return {'choices': [{'finish_reason': self.finish, 'message': {'content': self.content}}]}


class RuntimeTests(unittest.TestCase):
    def test_models_dir_from_environment(self):
        with tempfile.TemporaryDirectory() as folder:
            os.environ['AGENT_MODELS_DIR'] = folder
            try:
                self.assertEqual(local_llm.models_dir(), Path(folder))
                with self.assertRaises(FileNotFoundError):
                    local_llm.require('embed')
                # Only the small model is downloaded - use it.
                local_llm.model_path('chat-small').write_bytes(b'')
                self.assertEqual(local_llm.chat_model_name(), 'chat-small')
            finally:
                del os.environ['AGENT_MODELS_DIR']

    def test_clean_answer(self):
        response = FakeModel('<think>\n\n</think>\n\nAnswer').create_chat_completion()
        self.assertEqual(local_llm.clean_answer(response), 'Answer')
        with self.assertRaises(ValueError):
            local_llm.clean_answer(FakeModel('Cut off', 'length').create_chat_completion())
        with self.assertRaises(ValueError):
            local_llm.clean_answer(FakeModel('<think>x</think>').create_chat_completion())

    def test_ask_text_and_schema(self):
        model = FakeModel('Text')
        self.assertEqual(local_llm.ask(model, 'Rule', 'Data'), 'Text')
        settings = model.calls[0]
        self.assertEqual(settings['messages'], [{'role': 'system', 'content': 'Rule /no_think'},
                                                {'role': 'user', 'content': 'Data'}])
        self.assertNotIn('response_format', settings)
        schema = {'type': 'object', 'properties': {'n': {'type': 'integer'}}}
        model = FakeModel('{"n": 3}')
        self.assertEqual(local_llm.ask(model, 'R', 'D', schema=schema, max_tokens=8), {'n': 3})
        self.assertEqual(model.calls[0]['response_format'], {'type': 'json_object', 'schema': schema})
        self.assertEqual(model.calls[0]['max_tokens'], 8)

    def test_catalog(self):
        for name, (filename, url, size) in local_llm.MODELS.items():
            self.assertTrue(url.startswith('https://huggingface.co/') and url.endswith(filename), name)
            self.assertGreater(size, 0)


if __name__ == '__main__':
    unittest.main()
