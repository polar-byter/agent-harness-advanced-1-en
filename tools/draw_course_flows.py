"""Draw the lesson animations: what happens to the data at each step.

These are drawn scenes, not screen recordings. The texts and numbers come from the runs quoted in the lessons.
Each scene is a GIF 480 px wide and a static PNG with the final state.
"""
import argparse
import math
import runpy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 480, 360
FONTS = Path('C:/Windows/Fonts')
PAPER = '#f3f7fa'
INK = '#21384c'
MUTED = '#587083'
LINE = '#cbd8e1'
CARD = '#ffffff'
GREEN = '#147c70'
GREEN_BG = '#dcefe9'
BLUE = '#315bb0'
BLUE_BG = '#e1e9f7'
RED = '#b23a2e'
RED_BG = '#f7dcd6'
YELLOW = '#f6e3a1'
ORANGE = '#d9822b'
CATEGORY = {'kitchen': '#d9822b', 'noise': '#7d5bb0', 'affection': '#d0607e', 'hunting': '#3f8f4f', 'damage': '#b23a2e'}


def font(size, kind='ui'):
    name = {'ui': 'segoeui.ttf', 'bold': 'segoeuib.ttf', 'mono': 'consola.ttf', 'monob': 'consolab.ttf'}[kind]
    return ImageFont.truetype(str(FONTS / name), size)


F = {'title': font(19, 'bold'), 'h': font(14, 'bold'), 'ui': font(13), 'small': font(11),
     'mono': font(12, 'mono'), 'monob': font(13, 'monob'), 'big': font(16, 'bold')}


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return a + (b - a) * ease(t)


class Frame:
    def __init__(self, title, footer=''):
        self.image = Image.new('RGB', (W, H), PAPER)
        self.d = ImageDraw.Draw(self.image)
        self.d.text((16, 10), title, font=F['title'], fill=INK)
        if footer:
            self.d.text((16, H - 22), footer, font=F['small'], fill=MUTED)

    def text(self, xy, text, kind='ui', fill=INK, anchor='la'):
        assert self.d.textlength(text, font=F[kind]) <= W, text
        self.d.text(xy, text, font=F[kind], fill=fill, anchor=anchor)

    def fit(self, xy, text, kind, width, fill=INK):
        """Text within a width: if it does not fit, cut it with three dots."""
        selected = F[kind]
        while self.d.textlength(text, font=selected) > width and len(text) > 4:
            text = text[:-4].rstrip() + '...'
        self.d.text(xy, text, font=selected, fill=fill)

    def box(self, box, fill=CARD, outline=LINE, width=1, radius=8):
        self.d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

    def label(self, xy, text, fill=GREEN, bg=GREEN_BG, kind='small'):
        x, y = xy
        length = self.d.textlength(text, font=F[kind])
        self.d.rounded_rectangle((x, y, x + length + 12, y + F[kind].size + 7), radius=8, fill=bg, outline=fill)
        self.d.text((x + 6, y + 2), text, font=F[kind], fill=fill)
        return x + length + 12

    def arrow(self, start, end, color=MUTED, width=2, dashed=False):
        if dashed:
            steps = int(math.dist(start, end) // 8)
            for i in range(0, steps, 2):
                a = (mix(start[0], end[0], i / steps), mix(start[1], end[1], i / steps))
                b = (start[0] + (end[0] - start[0]) * (i + 1) / steps, start[1] + (end[1] - start[1]) * (i + 1) / steps)
                self.d.line((a, b), fill=color, width=width)
        else:
            self.d.line((start, end), fill=color, width=width)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        for side in (-0.5, 0.5):
            self.d.line((end, (end[0] - 9 * math.cos(angle + side), end[1] - 9 * math.sin(angle + side))),
                        fill=color, width=width)

    def chip(self, center, title, subtitle='', fill=BLUE):
        x, y = center
        self.box((x - 52, y - 24, x + 52, y + 24), fill=fill, outline=fill, radius=10)
        for i in range(5):
            self.d.line((x - 40 + i * 20, y - 30, x - 40 + i * 20, y - 24), fill=fill, width=2)
            self.d.line((x - 40 + i * 20, y + 24, x - 40 + i * 20, y + 30), fill=fill, width=2)
        self.text((x, y - 6 if subtitle else y), title, 'h', 'white', 'mm')
        if subtitle:
            self.text((x, y + 11), subtitle, 'small', '#dfe7f7', 'mm')

    def person(self, center, color=INK):
        x, y = center
        self.d.ellipse((x - 9, y - 22, x + 9, y - 4), fill=color)
        self.d.pieslice((x - 16, y - 2, x + 16, y + 30), 180, 360, fill=color)

    def check(self, xy, ok=True):
        x, y = xy
        if ok:
            self.d.line(((x, y + 6), (x + 5, y + 11), (x + 13, y + 1)), fill=GREEN, width=3)
        else:
            self.d.line(((x, y), (x + 11, y + 11)), fill=RED, width=3)
            self.d.line(((x + 11, y), (x, y + 11)), fill=RED, width=3)

    def window(self, box, title):
        x0, y0, x1, y1 = box
        self.box(box)
        self.d.rounded_rectangle((x0, y0, x1, y0 + 20), radius=8, fill='#e4ebf0')
        self.d.rectangle((x0, y0 + 10, x1, y0 + 20), fill='#e4ebf0')
        for i, color in enumerate(['#d9776a', '#e5bf5d', '#8bbf7a']):
            self.d.ellipse((x0 + 8 + i * 12, y0 + 6, x0 + 15 + i * 12, y0 + 13), fill=color)
        self.text((x0 + 50, y0 + 3), title, 'small', MUTED)


class Film:
    """The frames of one animation and the static picture."""

    def __init__(self):
        self.frames = []

    def add(self, frame, duration=90):
        self.frames.append((frame.image, duration))

    def hold(self, frame, duration=1800):
        self.add(frame, duration)


# ------------------------------------------------------------------ lesson 1

def lesson_01(data):
    film = Film()
    title = 'Lesson 1. The model moves into the program'

    def scene(move, crossed, tokens_shown, packet=None, caption=''):
        f = Frame(title, caption)
        f.window((16, 50, 300, 320), 'demo.py - your program')
        cloud_alpha = INK if move < 1 else LINE
        for cx, cy, r in ((380, 95, 28), (410, 85, 32), (440, 100, 24), (405, 110, 30)):
            f.d.ellipse((cx - r, cy - r, cx + r, cy + r), fill='#dce7ef' if move < 1 else '#edf2f5')
        f.text((410, 140), 'model service', 'small', cloud_alpha, 'mm')
        f.arrow((300, 100), (352, 100), MUTED if not crossed else LINE, dashed=True)
        if crossed:
            f.check((318, 92), ok=False)
            f.text((326, 160), 'no network needed', 'small', RED, 'mm')
        x = mix(408, 158, move)
        y = mix(98, 150, move)
        f.chip((x, y), 'Qwen3', '1.7B in memory' if move >= 1 else 'far away')
        if packet:
            label, fraction = packet
            px = mix(120, 340, fraction)
            f.label((px - 30, 84), label, BLUE, BLUE_BG)
        if move < 1:
            f.text((30, 200), 'send_live(question)', 'monob', INK)
            f.text((30, 222), 'a network request and waiting...', 'small', MUTED)
        if move >= 1:
            f.box((30, 200, 286, 228), fill=YELLOW, outline=YELLOW)
            f.text((40, 205), data['question'], 'ui')
            f.text((158, 182), 'ask(model, rule, question, schema=DAYS)', 'small', MUTED, 'mm')
            f.box((30, 240, 286, 280), fill=GREEN_BG, outline=GREEN)
            text = ''.join(data['tokens'][:tokens_shown])
            f.text((40, 250), text + ('_' if tokens_shown < len(data['tokens']) else ''), 'monob', GREEN)
            if tokens_shown == len(data['tokens']):
                f.text((40, 286), data['result'], 'monob', INK)
                f.text((40, 304), 'the schema let only a number through', 'small', MUTED)
        return f

    for i in range(12):
        film.add(scene(0, False, 0, ('question', i / 11), 'Main course: the question went over the network'))
    film.hold(scene(0, False, 0, None, 'Main course: the question went over the network'), 900)
    for i in range(14):
        film.add(scene(i / 13, i > 6, 0, None, 'Now the model file is loaded into the program memory'))
    film.hold(scene(1, True, 0, None, 'Now the model file is loaded into the program memory'), 1000)
    for count in range(len(data['tokens']) + 1):
        film.add(scene(1, True, count, None, 'The model writes token by token, the schema keeps the shape'), 450)
    final = scene(1, True, len(data['tokens']), None, 'A Python dictionary, not a byte left the computer')
    film.hold(final, 3000)
    return film, final


# ------------------------------------------------------------------ lesson 2

def cat(f, center, mood=0):
    x, y = center
    fur = '#e0a35a'
    f.d.polygon([(x - 26, y - 10), (x - 20, y - 36), (x - 6, y - 20)], fill=fur)
    f.d.polygon([(x + 26, y - 10), (x + 20, y - 36), (x + 6, y - 20)], fill=fur)
    f.d.ellipse((x - 30, y - 26, x + 30, y + 24), fill=fur)
    eye = 2 if mood % 2 else 6
    f.d.ellipse((x - 14, y - 8 - eye // 2, x - 6, y - 8 + eye // 2 + 2), fill=INK)
    f.d.ellipse((x + 6, y - 8 - eye // 2, x + 14, y - 8 + eye // 2 + 2), fill=INK)
    f.d.polygon([(x - 4, y + 2), (x + 4, y + 2), (x, y + 7)], fill='#c45a6a')
    for side in (-1, 1):
        for dy in (4, 9):
            f.d.line((x + side * 8, y + dy, x + side * 34, y + dy - 3 + dy // 3), fill=INK, width=1)


def lesson_02(data):
    film = Film()
    title = 'Lesson 2. The model sorts the cat journal'
    rows = data['rows']

    def scene(done, flying=None, bars=0.0, paper=False, caption=''):
        f = Frame(title, caption)
        f.window((16, 50, 316, 286), 'journal.xlsx - sheet "Journal"')
        for i, (text, category, severity) in enumerate(rows):
            y = 80 + i * 40
            f.box((24, y, 308, y + 32), fill='#fbfdfe' if i != done else YELLOW, outline=LINE, radius=4)
            f.fit((32, y + 8), text, 'ui', 180)
            if i < done:
                f.label((220, y + 6), f'{category} {severity}', CATEGORY[category], '#ffffff')
        cat(f, (392, 92), done)
        f.chip((392, 168), 'Qwen3', 'classify_entry')
        if flying is not None:
            index, fraction = flying
            text, category, severity = rows[index]
            x = mix(340, 220, fraction)
            y = mix(168, 86 + index * 40, fraction)
            f.label((x, y), f'{category} {severity}', CATEGORY[category], '#ffffff')
        if bars:
            f.box((326, 214, 464, 330), outline=LINE)
            for i, (category, count) in enumerate(data['counts'].items()):
                y = 222 + i * 21
                f.text((334, y), category, 'small', MUTED)
                f.d.rounded_rectangle((394, y + 2, 394 + 20 * count * bars, y + 14), radius=4, fill=CATEGORY[category])
        if paper:
            f.box((16, 294, 316, 324), fill='#fffaf0', outline=ORANGE)
            f.text((26, 299), 'Evening news: a bulletin for the family', 'h', ORANGE)
        return f

    for index in range(len(rows)):
        for step in range(7):
            film.add(scene(index, (index, step / 6), caption='The model sorts each entry on its own'))
        film.add(scene(index + 1, caption='Only five categories are allowed: enum in the schema'), 500)
    for step in range(10):
        film.add(scene(len(rows), bars=(step + 1) / 10, caption='The count over all twelve entries'))
    final = scene(len(rows), bars=1, paper=True, caption='The model writes a bulletin, the program saves the "Review" sheet')
    film.hold(final, 3000)
    return film, final


# ------------------------------------------------------------------ lesson 3

def lesson_03(data):
    film = Film()
    title = 'Lesson 3. The model scores, the program decides'
    options, threshold = data['options'], data['threshold']
    left, right = 110, 420
    places = {'person': (150, 312), 'delivery': (390, 312)}

    def scene(case, grow, slide=0.0, parked=(), caption='', rule=False):
        number, text, values, decision = data['cases'][case]
        f = Frame(title, caption)
        f.box((16, 290, 230, 334), fill='#eef3f6', outline=LINE)
        f.person((40, 312))
        f.text((60, 296), 'operator', 'small', MUTED)
        f.box((250, 290, 464, 334), fill=GREEN_BG, outline=GREEN)
        f.text((262, 296), 'delivery queue', 'small', GREEN)
        for i, (option, value) in enumerate(zip(options, values)):
            y = 98 + i * 27
            f.text((16, y), option, 'ui', MUTED)
            f.box((left, y + 2, right, y + 18), fill='#e7eef2', outline='#e7eef2', radius=4)
            length = (right - left) * value * ease(grow)
            if length > 2:
                f.d.rounded_rectangle((left, y + 2, left + length, y + 18), radius=4,
                                      fill=GREEN if value >= threshold else BLUE)
            if grow >= 1 and value > 0.05:
                f.text((left + length + 6, y + 2), f'{value:.2f}', 'h', INK)
        x = left + (right - left) * threshold
        for y in range(92, 262, 8):
            f.d.line((x, y, x, y + 4), fill=RED, width=2)
        f.text((x, 270), 'threshold 0.9', 'h', RED, 'mm')
        if rule:
            f.box((16, 236, 300, 262), fill=RED_BG, outline=RED)
            f.text((24, 241), data['rule'], 'small', RED)
        for label, place in parked:
            px, py = places[place]
            f.label((px - 22, py - 4), label, ORANGE, YELLOW)
        px, py = places[decision]
        x0, y0 = mix(16, px - 22, slide), mix(48, py - 4, slide)
        x1, y1 = mix(464, px + 30, slide), mix(82, py + 16, slide)
        f.box((x0, y0, x1, y1), fill=YELLOW, outline=ORANGE)
        if slide < 0.5:
            f.fit((x0 + 8, y0 + 8), f'{number}  {text}', 'ui', x1 - x0 - 16)
        else:
            f.text((x0 + 6, y0 + 2), number, 'small', ORANGE)
        return f

    film.hold(scene(0, 0, caption='A request and a question: which queue?'), 1200)
    for i in range(12):
        film.add(scene(0, i / 11, caption='First-token scores become probabilities'))
    film.hold(scene(0, 1, caption='Delivery 1.00 - above the threshold'), 1500)
    for i in range(10):
        film.add(scene(0, 1, i / 9, caption='The program sends it to the queue itself'))
    parked = ((data['cases'][0][0], 'delivery'),)
    for i in range(12):
        film.add(scene(1, i / 11, parked=parked, caption='The next request'))
    film.hold(scene(1, 1, parked=parked, caption='Payment 1.00 - confident, but wrong'), 1800)
    film.hold(scene(1, 1, parked=parked, caption='The second question: not about an order', rule=True), 1800)
    for i in range(10):
        film.add(scene(1, 1, i / 9, parked, 'The store rule in code sends it to a person', True))
    final = scene(1, 1, 1, parked, 'Threshold and rules in code decide, the model only scores', True)
    film.hold(final, 3000)
    return film, final


# ------------------------------------------------------------------ lesson 4

def phone_photo(f, box, alpha=1.0):
    x0, y0, x1, y1 = box
    f.box(box, fill='#d7e3ea', outline=LINE, radius=4)
    f.d.rounded_rectangle((x0 + 38, y0 + 14, x1 - 38, y1 - 14), radius=12, fill='#1f2a33')
    f.d.rounded_rectangle((x0 + 46, y0 + 26, x1 - 46, y1 - 26), radius=4, fill='#4b6b85')
    cx, cy = (x0 + x1) // 2 + 8, y0 + 70
    for dx, dy in ((-30, -30), (26, -40), (34, 22), (-22, 44), (4, 60)):
        f.d.line((cx, cy, cx + dx, cy + dy), fill='#e8f0f5', width=2)


def lesson_04(data):
    film = Film()
    title = 'Lesson 4. A vision model looks at the photo'
    photo = (16, 80, 176, 250)
    cols, rows = 4, 5
    cells = [(c, r) for r in range(rows) for c in range(cols)]

    def scene(grid, flown, answer, routed, caption=''):
        f = Frame(title, caption)
        f.text((16, 50), data['claim'], 'h', INK)
        phone_photo(f, photo)
        cw = (photo[2] - photo[0]) / cols
        ch = (photo[3] - photo[1]) / rows
        if grid:
            for c in range(1, cols):
                f.d.line((photo[0] + c * cw, photo[1], photo[0] + c * cw, photo[3]), fill='#ffffff', width=2)
            for r in range(1, rows):
                f.d.line((photo[0], photo[1] + r * ch, photo[2], photo[1] + r * ch), fill='#ffffff', width=2)
        f.box((200, 92, 290, 150), fill=BLUE_BG, outline=BLUE)
        f.text((245, 112), 'projector', 'h', BLUE, 'mm')
        f.text((245, 130), 'patches -> numbers', 'small', BLUE, 'mm')
        f.chip((245, 205), 'Qwen3-VL', 'language part')
        for index in range(int(flown)):
            c, r = cells[index]
            f.d.rectangle((300 + (index % 10) * 16, 96 + (index // 10) * 16, 312 + (index % 10) * 16,
                           108 + (index // 10) * 16), fill=BLUE)
        if flown % 1:
            c, r = cells[int(flown)]
            t = flown % 1
            x = mix(photo[0] + c * cw + cw / 2, 245, t)
            y = mix(photo[1] + r * ch + ch / 2, 120, t)
            f.d.rectangle((x - 6, y - 6, x + 6, y + 6), fill='#4b6b85', outline='white')
        if flown >= len(cells):
            f.text((300, 136), 'the picture became numbers', 'small', MUTED)
        for i, (field, value) in enumerate(data['answer'][:answer]):
            y = 168 + i * 24
            f.text((306, y), f'{field}: {value}', 'monob', INK)
        if routed:
            f.box((16, 280, 464, 314), fill=RED_BG, outline=RED)
            f.text((26, 288), data['route'], 'ui', RED)
        return f

    film.hold(scene(False, 0, 0, False, 'The customer ordered a kettle and attached a photo'), 1400)
    film.hold(scene(True, 0, 0, False, 'The projector cuts the picture into patches'), 1000)
    for i in range(len(cells) * 2 + 1):
        film.add(scene(True, i / 2, 0, False, 'Each patch turns into numbers'), 70)
    for count in range(1, len(data['answer']) + 1):
        film.hold(scene(True, len(cells), count, False, 'First the model names the item, then compares'), 900)
    final = scene(True, len(cells), len(data['answer']), True, 'The program picks the route by the yes/no fields')
    film.hold(final, 3000)
    return film, final


# ------------------------------------------------------------------ lesson 5

def lesson_05(data):
    film = Film()
    title = 'Lesson 5. Search by meaning: nearby points'
    query = data['query']
    qx, qy = data['query_point']

    def scene(typed, star, ring, found, caption=''):
        f = Frame(title, caption)
        f.box((16, 46, 464, 74), fill=CARD, outline=BLUE)
        f.text((26, 52), 'Search: ' + query[:typed] + ('|' if typed < len(query) else ''), 'ui', INK)
        f.box((16, 84, 464, 330), fill='#fbfdfe', outline=LINE)
        for title_, (x, y) in data['movies']:
            hit = title_ in data['found'][:found]
            f.d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=GREEN if hit else MUTED)
            f.fit((x + 8, y - 8), title_, 'h' if hit else 'small', min(200, 456 - x), GREEN if hit else MUTED)
            if hit:
                f.d.line((qx, qy, x, y), fill=GREEN, width=2)
        if star:
            points = []
            for k in range(10):
                r = 10 if k % 2 == 0 else 4
                a = -math.pi / 2 + k * math.pi / 5
                points.append((qx + r * math.cos(a), qy + r * math.sin(a)))
            f.d.polygon(points, fill=ORANGE)
            f.text((qx - 12, qy + 14), 'query', 'small', ORANGE)
        if ring:
            r = 20 + 90 * ring
            f.d.ellipse((qx - r, qy - r, qx + r, qy + r), outline=ORANGE, width=2)
        return f

    for i in range(len(query) + 1):
        film.add(scene(i, False, 0, 0, 'The model turns each description into a point'), 70)
    film.hold(scene(len(query), True, 0, 0, 'The query becomes a point too'), 1200)
    for i in range(10):
        film.add(scene(len(query), True, (i + 1) / 10, 0, 'Looking for the nearest points'), 90)
    for count in range(1, len(data['found']) + 1):
        film.hold(scene(len(query), True, 0, count, data['nearest']), 900)
    final = scene(len(query), True, 0, len(data['found']), 'The positions are illustrative: real vectors have 1024 numbers')
    film.hold(final, 3000)
    return film, final


# ------------------------------------------------------------------ lesson 6

def wave(f, box, played):
    x0, y0, x1, y1 = box
    mid = (y0 + y1) / 2
    for x in range(int(x0), int(x1), 3):
        t = (x - x0) / (x1 - x0)
        amplitude = (y1 - y0) / 2 * (0.25 + 0.75 * abs(math.sin(t * 23) * math.sin(t * 7.3 + 1)))
        if (int(t * 70) % 9) == 0:
            amplitude *= 0.15
        color = BLUE if t <= played else '#b9c8d4'
        f.d.line((x, mid - amplitude, x, mid + amplitude), fill=color, width=2)


def lesson_06(data):
    film = Film()
    title = 'Lesson 6. Voice message -> request card'
    total = data['seconds']

    def scene(played, card, caption=''):
        f = Frame(title, caption)
        f.box((16, 46, 464, 100), fill=CARD, outline=LINE)
        wave(f, (26, 54, 454, 92), played)
        x = 26 + 428 * played
        f.d.line((x, 50, x, 96), fill=RED, width=2)
        f.text((454, 104), f'{played * total:4.1f} s of {total}', 'small', MUTED, 'ra')
        shown = [line for start, line in data['lines'] if start <= played * total]
        f.box((16, 120, 300 if card else 464, 330), fill='#fbfdfe', outline=LINE)
        for i, line in enumerate(shown):
            f.fit((24, 128 + i * 28), line, 'ui', (268 if card else 432))
        if card:
            f.box((310, 120, 464, 330), fill=GREEN_BG, outline=GREEN)
            f.text((320, 126), 'Request card', 'h', GREEN)
            for i, (field, value) in enumerate(data['card'][:card]):
                y = 152 + i * 42
                f.text((320, y), field, 'small', MUTED)
                f.fit((320, y + 15), value, 'h', 136)
        return f

    for i in range(31):
        film.add(scene(i / 30, 0, 'Whisper listens and writes segments with timestamps'), 110)
    film.hold(scene(1, 0, 'The transcript is ready'), 1200)
    for count in range(1, len(data['card']) + 1):
        film.hold(scene(1, count, 'Qwen3 fills in the card fields from the text'), 800)
    final = scene(1, len(data['card']), 'The operator sees the card and can replay the right spot')
    film.hold(final, 3000)
    return film, final


# ------------------------------------------------------------------ lesson 7

def bubble(f, box, text, mine):
    """A chat message: the text wraps by words and the height grows to fit."""
    x0, y0, x1, _ = box
    lines, line = [], ''
    for word in text.split():
        candidate = (line + ' ' + word).strip()
        if line and f.d.textlength(candidate, font=F['small']) > x1 - x0 - 14:
            lines.append(line)
            line = word
        else:
            line = candidate
    lines.append(line)
    bottom = y0 + 8 + len(lines) * 15
    f.box((x0, y0, x1, bottom), fill='#d9f2d0' if mine else CARD, outline=LINE, radius=10)
    for i, line in enumerate(lines):
        f.d.text((x0 + 8, y0 + 4 + i * 15), line, font=F['small'], fill=INK)
    return bottom


def lesson_07(data):
    film = Film()
    title = 'Lesson 7. Telegram message -> journal'
    who, text = data['family']
    guest, guest_text = data['stranger']

    def scene(step, fly=0.0, caption=''):
        f = Frame(title, caption)
        f.box((16, 46, 176, 330), fill='#1f2a33', outline='#1f2a33', radius=18)
        f.box((24, 60, 168, 316), fill='#eaf1f5', outline='#eaf1f5', radius=10)
        f.text((96, 70), 'Whiskers journal', 'small', MUTED, 'mm')
        f.window((210, 46, 464, 150), 'bot.py on the laptop')
        f.box((222, 76, 300, 140), fill=CARD, outline=LINE)
        f.text((261, 90), 'allow', 'small', MUTED, 'mm')
        f.text((261, 104), 'list', 'small', MUTED, 'mm')
        f.chip((382, 108), 'Qwen3', 'classify_entry')
        f.window((210, 170, 464, 250), 'journal.xlsx')
        f.box((220, 196, 454, 218), fill='#fbfdfe', outline=LINE, radius=3)
        f.text((226, 200), 'Dad  damage 2  Knocked headphones...', 'small', MUTED)
        y = 84
        if step >= 1:
            y = bubble(f, (30, y, 162, 0), f'{who}: {text}', True) + 8
        if step == 1:
            x = mix(160, 240, fly)
            f.d.rectangle((x - 10, 93, x + 10, 107), fill=YELLOW, outline=ORANGE)
        if step >= 2:
            f.check((242, 120))
        if step >= 3:
            f.box((220, 222, 454, 244), fill=YELLOW, outline=ORANGE, radius=3)
            row_who, category, severity = data['row']
            f.text((226, 226), f'{row_who}  {category} {severity}  Grabbed a sausage...', 'small', INK)
        if step >= 4:
            y = bubble(f, (30, y, 162, 0), data['reply'], False) + 8
        if step >= 5:
            y = bubble(f, (30, y, 162, 0), f'{guest}: {guest_text}', True) + 8
        if step >= 6:
            f.check((266, 120), ok=False)
            f.box((210, 262, 464, 330), fill=RED_BG, outline=RED)
            f.text((220, 270), 'id is not in allowed_users.txt', 'h', RED)
            f.text((220, 292), 'no model call, the journal stays as it was', 'small', RED)
        if step >= 7:
            bubble(f, (30, y, 162, 0), data['refusal'], False)
        return f

    film.hold(scene(0, caption='The bot waits for messages: long polling'), 1000)
    film.hold(scene(1, 0, 'Emma writes to the bot'), 900)
    for i in range(8):
        film.add(scene(1, i / 7, 'The message reaches bot.py'))
    film.hold(scene(2, caption='Emma\'s id is in the allow list'), 1000)
    film.hold(scene(3, caption='The model sorts the entry, a row goes to the journal'), 1200)
    film.hold(scene(4, caption='The bot replies in the chat'), 1500)
    film.hold(scene(5, caption='A stranger writes'), 1000)
    film.hold(scene(6, caption='The code checks access, not the model'), 1500)
    final = scene(7, caption='A polite refusal: only the family can add entries')
    film.hold(final, 3000)
    return film, final


SCENES = [('lesson-01-ask', lesson_01, 'LESSON_01'), ('lesson-02-journal', lesson_02, 'LESSON_02'),
          ('lesson-03-decisions', lesson_03, 'LESSON_03'), ('lesson-04-photo', lesson_04, 'LESSON_04'),
          ('lesson-05-service', lesson_05, 'LESSON_05'), ('lesson-06-speech', lesson_06, 'LESSON_06'),
          ('lesson-07-bot', lesson_07, 'LESSON_07')]


def save(destination, film, final):
    destination.parent.mkdir(parents=True, exist_ok=True)
    final.image.save(destination.with_suffix('.png'))
    images = [image.convert('P', palette=Image.Palette.ADAPTIVE, colors=96) for image, _ in film.frames]
    images[0].save(destination, save_all=True, append_images=images[1:],
                   duration=[duration for _, duration in film.frames], loop=0, disposal=2, optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', help='Part of a file name to draw one picture')
    parser.add_argument('--out', type=Path, default=ROOT / 'assets', help='Folder for the GIF and PNG files')
    args = parser.parse_args()
    examples = runpy.run_path(str(Path(__file__).with_name('course_flow_examples.py')))
    for name, draw, key in SCENES:
        if args.only and args.only not in name:
            continue
        film, final = draw(examples[key])
        save(args.out / (name + '.gif'), film, final)
        print(name, len(film.frames), 'frames')


if __name__ == '__main__':
    main()
