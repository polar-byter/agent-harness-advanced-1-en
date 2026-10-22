"""The same questions for the real Jev: an HTTP request to the TypeSafe AI API.

Needs an API key in the TYPESAFE_API_KEY environment variable. The request text goes to TypeSafe's
servers, so send only data you are allowed to share outside.
"""
import json
import os
import urllib.request

API_URL = 'https://api.typesafe.ai/v1/systemone'


def ask_jev(state, questions: dict, model: str = 'jev-latest', api_key: str | None = None,
            url: str = API_URL) -> dict:
    """Return the answers dictionary from Jev's response: the same keys as decide."""
    key = api_key or os.environ.get('TYPESAFE_API_KEY')
    if not key:
        raise ValueError('No API key: set the TYPESAFE_API_KEY environment variable')
    body = json.dumps({'state': state, 'model': model, 'questions': questions}, ensure_ascii=False)
    request = urllib.request.Request(url, data=body.encode('utf-8'), method='POST', headers={
        'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))['answers']
