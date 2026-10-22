"""Build the lesson starters from maintainer/starters, unpack them into exercises and zip them into downloads.

A starter = the lesson's source files + the shared local_llm.py + get_models.py, requirements.txt,
.gitignore and TASK.md, which is assembled from the lesson page in course/.
"""
import json
import re
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
STARTERS = ROOT / 'maintainer' / 'starters'
SOLUTIONS = ROOT / 'maintainer' / 'solutions'
RUNTIME = ROOT / 'tools' / 'model_runtime' / 'local_llm.py'
STUB = re.compile(r'^( +)# [^\n]*\n\1raise NotImplementedError\([^\n]*\)\n', re.M)
TASK_SECTIONS = ('Your turn', 'Connect', 'Guess', 'Run', 'Try to break it')
GITIGNORE = '.venv/\n.idea/\n__pycache__/\n*.db\ndata/demo-journal.xlsx\n'

GET_MODELS = '''"""Downloads this lesson's models into the shared course models folder."""
import sys

from local_llm import download, models_dir

MODELS = {models}


def main():
    print('Models folder:', models_dir())
    # Run with the parameter small downloads the small language model instead of the main one.
    small = 'small' in sys.argv[1:]
    download(*[('chat-small' if small and name == 'chat' else name) for name in MODELS])


if __name__ == '__main__':
    main()
'''


def load_config() -> dict:
    return json.loads((ROOT / 'tools' / 'course-map.json').read_text(encoding='utf-8'))


def apply_solution(text: str, block: str) -> str:
    """Replace the first stub (a comment + raise NotImplementedError) with the reference code."""
    replaced, count = STUB.subn(block if block.endswith('\n') else block + '\n', text, count=1)
    assert count == 1, 'Stub not found'
    return replaced


def solved_file(root: str, relative: str, text: str) -> str:
    """Reference solution: a .txt block replaces the stub, a file without .txt replaces the source entirely."""
    whole = SOLUTIONS / root / relative
    if whole.is_file():
        return whole.read_text(encoding='utf-8')
    block = SOLUTIONS / root / (relative + '.txt')
    return apply_solution(text, block.read_text(encoding='utf-8')) if block.is_file() else text


def plain_text(markdown: str) -> str:
    """Images and relative links do not work inside a starter, so we keep only the link text."""
    markdown = re.sub(r'^<img [^\n]*\n?', '', markdown, flags=re.M)
    markdown = re.sub(r'^\[Static version\]\([^)]*\)\.?\n?', '', markdown, flags=re.M)
    return re.sub(r'\[([^\]]+)\]\((?!https?://)[^)]+\)', r'\1', markdown)


def task_text(lesson: dict) -> str:
    """TASK.md: "Where we are" and the practical sections of the lesson, without the long explanations."""
    text = (ROOT / lesson['path']).read_text(encoding='utf-8')
    where = re.search(r'^> \*\*Where we are\.\*\*.*?(?=\n\n)', text, re.M | re.S)
    parts = [f"# Hints for lesson {lesson['number']}. {lesson['title']}", '']
    if where:
        parts += [where.group(0), '']
    targets = ', '.join(f'`{file}` -> `{name}`' for file, name in lesson['targets'])
    parts += ['Current task: ' + targets + '. The full lesson: ' + lesson['path'] + ' in the course repository.', '']
    for section in re.split(r'(?m)^(?=## )', text):
        heading = section.splitlines()[0][3:] if section.startswith('## ') else ''
        if heading.startswith(TASK_SECTIONS):
            parts.append(section.strip())
            parts.append('')
    return re.sub(r'\n{3,}', '\n\n', plain_text('\n'.join(parts))).strip() + '\n'


def assemble(lesson: dict, config: dict) -> dict[str, bytes]:
    root = lesson['root']
    files = {}
    for path in sorted((STARTERS / root).rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            files[path.relative_to(STARTERS / root).as_posix()] = path.read_bytes()
    if not lesson.get('own_runtime'):
        files['local_llm.py'] = RUNTIME.read_bytes()
    for name, source in lesson.get('shared', {}).items():
        text = (STARTERS / source / name).read_text(encoding='utf-8')
        files[name] = solved_file(source, name, text).encode('utf-8')
    files['get_models.py'] = GET_MODELS.format(models=lesson['models']).encode('utf-8')
    lines = [line for group in lesson['requirements'] for line in config['requirements'][group]]
    files['requirements.txt'] = ('\n'.join(lines) + '\n').encode('utf-8')
    files['.gitignore'] = GITIGNORE.encode('utf-8')
    files['TASK.md'] = task_text(lesson).encode('utf-8')
    return {name: data.replace(b'\r\n', b'\n') if not name.endswith(('.jpg', '.wav', '.xlsx')) else data
            for name, data in files.items()}


def write_zip(destination: Path, root: str, files: dict[str, bytes]) -> None:
    """A fixed date inside the archive: with unchanged files the ZIP stays byte for byte the same."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, 'w', ZIP_DEFLATED) as archive:
        for name in sorted(files):
            info = ZipInfo(f'{root}/{name}', date_time=(2026, 10, 22, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, files[name])


def unpack(folder: Path, files: dict[str, bytes]) -> None:
    if folder.exists():
        shutil.rmtree(folder)
    for name, data in files.items():
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def main():
    config = load_config()
    for lesson in config['lessons']:
        files = assemble(lesson, config)
        write_zip(ROOT / 'downloads' / (lesson['root'] + '.zip'), lesson['root'], files)
        unpack(ROOT / 'exercises' / lesson['root'], files)
        print(lesson['root'], len(files), 'files')


if __name__ == '__main__':
    main()
