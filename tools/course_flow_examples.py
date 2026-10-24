"""Data for the lesson animations. The numbers and texts come from the runs quoted in the lessons."""

LESSON_01 = {
    'question': 'How many days do I have to return an item?',
    'tokens': ['{"', 'days', '":', ' 14', '}'],
    'result': "data = {'days': 14}",
}

LESSON_02 = {
    'rows': [
        ('Stole a meatball from the table', 'kitchen', 3),
        ('Yowled outside the bedroom door', 'noise', 3),
        ('Fell asleep on my lap and purred', 'affection', 1),
        ('Caught a fly, left it in a slipper', 'hunting', 1),
        ('Clawed the new curtain to shreds', 'damage', 3),
    ],
    'counts': {'noise': 3, 'hunting': 3, 'damage': 3, 'affection': 2, 'kitchen': 1},
}

LESSON_03 = {
    'options': ['returns', 'complaints', 'delivery', 'payment', 'account', 'other'],
    'threshold': 0.9,
    'cases': [
        ('R-104', 'The courier was three hours late', [0.0, 0.0, 1.0, 0.0, 0.0, 0.0], 'delivery'),
        ('R-118', 'Hello, do you sell gift cards?', [0.0, 0.0, 0.0, 1.0, 0.0, 0.0], 'person'),
    ],
    'rule': 'payment, but not about an order -> person',
}

LESSON_04 = {
    'claim': 'A-1046: an electric kettle was ordered',
    'answer': [('item', '"phone"'), ('same_item', 'false'), ('damage_visible', 'true')],
    'route': 'ask for another photo: not the ordered item',
}

LESSON_05 = {
    'query': 'hockey movie',
    # The positions are illustrative: real vectors have 1024 numbers and cannot be drawn on a plane.
    'movies': [
        ('Miracle', (300, 150)), ('The Snowman', (250, 205)),
        ('Galaxy Quest', (345, 230)), ('Battle of Britain', (110, 140)),
        ('Back to the Future', (95, 225)), ('WALL-E', (150, 270)),
        ('The Apartment', (195, 165)), ('Groundhog Day', (40, 285)),
        ('The Hound of the Baskervilles', (240, 305)), ('When Harry Met Sally...', (40, 105)),
    ],
    'query_point': (330, 175),
    'found': ['Miracle', 'The Snowman', 'Galaxy Quest'],
    'nearest': '"Miracle" is closest, though no description says "hockey"',
}

LESSON_06 = {
    'seconds': 20.9,
    'lines': [
        (0.0, '[00:00] Hello. My name is Olivia Parker, order number 4512.'),
        (6.0, '[00:06] Two weeks ago I bought an electric kettle from you,'),
        (8.5, '        and yesterday it stopped switching on.'),
        (12.0, '[00:12] I would like my money back.'),
        (15.0, '[00:15] I still have the receipt.'),
        (17.0, '[00:17] Please call me back after six in the evening.'),
    ],
    'card': [('name', 'Olivia Parker'), ('order', '4512'), ('wish', 'refund'), ('callback', 'after six in the evening')],
}

LESSON_07 = {
    'family': ('Emma', 'Grabbed a sausage off the table while I was pouring tea'),
    'reply': 'Recorded in the journal: kitchen, severity 2.',
    'row': ('Emma', 'kitchen', 2),
    'stranger': ('Guest', 'Hi! Add me too'),
    'refusal': 'I only record mischief from family members.',
}
