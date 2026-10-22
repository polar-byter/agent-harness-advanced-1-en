"""Checking the photo from a return claim with a vision model."""
import base64
import json
from pathlib import Path

from local_llm import clean_answer

PHOTO_RULE = (
    'You help check product photos for return claims. First, name the object in the photo in item. '
    'Then answer in same_item whether it is the same product that was ordered. Then say whether damage '
    'is visible: cracks, chips, broken glass, dents. In comment write one short sentence in English.'
)
# The model fills the fields in order: first it names the object, then compares it with the order.
PHOTO_SCHEMA = {
    'type': 'object',
    'properties': {
        'item': {'type': 'string', 'maxLength': 60},
        'same_item': {'type': 'boolean'},
        'damage_visible': {'type': 'boolean'},
        'comment': {'type': 'string', 'maxLength': 200},
    },
    'required': ['item', 'same_item', 'damage_visible', 'comment'],
}


def read_returns(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding='utf-8'))


def image_to_data_uri(path: Path) -> str:
    """The picture travels inside the message: the file bytes are written as base64 text."""
    if not path.is_file():
        raise FileNotFoundError(f'Photo {path} is missing')
    return 'data:image/jpeg;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def check_photo(model, photo: Path, ordered_item: str) -> dict:
    # Pass the photo and the name of the ordered item to the model and get the answer by PHOTO_SCHEMA.
    raise NotImplementedError('Complete check_photo in photo_check.py using the lesson 4 hints')


def route_return(check: dict) -> str:
    """A staff member decides about the money; the model only helps sort the claims."""
    if not check['same_item']:
        return 'ask for another photo: the picture does not show the ordered item'
    if check['damage_visible']:
        return 'to staff: damage is visible in the photo'
    return 'to staff: no damage visible in the photo, the item needs checking'
