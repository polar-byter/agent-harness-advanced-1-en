import json
from pathlib import Path

from photo_check import check_photo, route_return

ROOT = Path(__file__).resolve().parent
PHOTO = ROOT / 'data' / 'photos' / 'phone.jpg'


class ExampleVisionModel:
    """A stand-in for the vision model: returns a prepared answer."""

    def __init__(self):
        self.calls = []

    def create_chat_completion(self, **settings):
        self.calls.append(settings)
        content = json.dumps({'item': 'smartphone', 'same_item': True, 'damage_visible': True,
                              'comment': 'The back panel of the smartphone is shattered.'})
        return {'choices': [{'finish_reason': 'stop', 'message': {'content': content}}]}


def check_exercise():
    model = ExampleVisionModel()
    check = check_photo(model, PHOTO, 'smartphone')
    parts = model.calls[0]['messages'][1]['content']
    assert parts[0]['type'] == 'image_url', 'The first part of the message is the picture'
    assert parts[0]['image_url']['url'].startswith('data:image/jpeg;base64,'), 'Pass the photo through image_to_data_uri'
    assert parts[1]['text'].endswith('smartphone'), 'Name the ordered item in the second part'
    assert 'schema' in model.calls[0]['response_format'], 'Restrict the answer with PHOTO_SCHEMA'
    return route_return(check)


def main():
    try:
        print('Offline check:', check_exercise())
    except NotImplementedError as error:
        print(error)


if __name__ == '__main__':
    main()
