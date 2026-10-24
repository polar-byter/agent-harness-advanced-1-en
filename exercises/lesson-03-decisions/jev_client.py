"""The same questions for the real Jev through OpenRouter.

The key comes from the OPENROUTER_API_KEY environment variable, and if it is not set, from the main
course connection that configure_model.py saves with the OpenRouter service. The request text goes to
OpenRouter and TypeSafe, so send only data you are allowed to share outside.
"""
import json
import os
import urllib.request
from pathlib import Path

API_URL = 'https://openrouter.ai/api/alpha/decisions'
MODEL = 'typesafe/jev-1.14'


def connection_path() -> Path:
    """The same connection file as in the main course."""
    override = os.environ.get('HARNESS_CONNECTION_FILE')
    if override:
        return Path(override)
    folder = Path(os.environ.get('LOCALAPPDATA', Path.home() / '.config'))
    return folder / 'AgentHarnessWorkshopEnglish' / 'connection.json'


def openrouter_key() -> str:
    key = os.environ.get('OPENROUTER_API_KEY')
    if key:
        return key
    path = connection_path()
    if path.is_file():
        settings = json.loads(path.read_text(encoding='utf-8'))
        if settings.get('provider') == 'openrouter' and settings.get('api_key'):
            return settings['api_key']
    raise ValueError('No OpenRouter key: set up the connection with configure_model.py from the main course '
                     'or set the OPENROUTER_API_KEY environment variable')


def ask_jev(state, questions: dict, model: str = MODEL, api_key: str | None = None,
            url: str = API_URL) -> dict:
    """Return the answers dictionary from Jev's response: the same keys as decide."""
    key = openrouter_key() if api_key is None else api_key
    if not key:
        raise ValueError('Empty OpenRouter key')
    body = json.dumps({'model': model, 'state': state, 'questions': questions}, ensure_ascii=False)
    request = urllib.request.Request(url, data=body.encode('utf-8'), method='POST', headers={
        'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode('utf-8'))['answers']
