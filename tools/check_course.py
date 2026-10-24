"""Check the course packaging without models and without a network.

Links and punctuation in Markdown, untranslated text, Python syntax, archives matching the exercises
folders, the shared local_llm.py module and unfinished demo_check.py and demo.py. Passing does not mean
the learner functions are implemented: tools/check_solutions.py covers the reference solutions.
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from build_starters import solved_file

ROOT = Path(__file__).resolve().parents[1]
SKIP = ('.git', '.checks', '.venv', 'maintainer')
TEXT = ('.py', '.md', '.json', '.txt', '.html')
CYRILLIC = re.compile('[\u0400-\u04ff]')


def check_markdown() -> tuple[int, int]:
    files = [path for path in ROOT.rglob('*.md') if not any(part in SKIP for part in path.relative_to(ROOT).parts)]
    files += [path for path in (ROOT / 'maintainer' / name for name in ('README.md', 'WORK_LOG.md')) if path.is_file()]
    links = 0
    for path in files:
        text = path.read_text(encoding='utf-8')
        special = sorted({char for char in text if ord(char) > 127 and unicodedata.category(char)[0] in 'PSZ'})
        assert not special, (path, 'Only keyboard punctuation', special)
        assert text.count('```') % 2 == 0, (path, 'Unclosed code block')
        for code in re.findall(r'```python\n(.*?)```', text, re.S):
            # Templates show a function body with indentation, so we remove the common indent.
            ast.parse(textwrap.dedent(code), filename=str(path))
        targets = re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', text) + re.findall(r'<img[^>]+src="([^"]+)"', text)
        for target in targets:
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path:
                continue
            resolved = (path.parent / unquote(url.path)).resolve()
            assert resolved.is_relative_to(ROOT) and resolved.exists(), (path, target)
            links += 1
        for width in re.findall(r'<img[^>]+width="(\d+)"', text):
            assert int(width) <= 600, (path, width)
    return len(files), links


def check_english() -> int:
    """No untranslated Russian text in the repository's text files."""
    count = 0
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix in TEXT and not any(part in ('.git', '.checks') for part in path.parts):
            assert not CYRILLIC.search(path.read_text(encoding='utf-8')), (path, 'Untranslated Cyrillic text')
            count += 1
    return count


def normalized(data: bytes, name: str) -> bytes:
    return data.replace(b'\r\n', b'\n') if name.endswith(TEXT) or name.endswith('.gitignore') else data


def run(folder: Path, module: str) -> str:
    result = subprocess.run([sys.executable, '-B', '-c', f'import {module}; {module}.main()'], cwd=folder,
                            capture_output=True, text=True, encoding='utf-8', timeout=60,
                            env=dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1'))
    assert result.returncode == 0, (folder.name, module, result.stdout, result.stderr)
    return result.stdout


def main():
    config = json.loads((ROOT / 'tools' / 'course-map.json').read_text(encoding='utf-8'))
    for document in config['documents']:
        assert (ROOT / document['path']).is_file(), document['path']
    pages, links = check_markdown()
    text_files = check_english()
    runtime = (ROOT / 'tools' / 'model_runtime' / 'local_llm.py').read_bytes()
    python_files = 0
    scratch = ROOT / '.checks'
    scratch.mkdir(exist_ok=True)
    for lesson in config['lessons']:
        exercise = ROOT / 'exercises' / lesson['root']
        assert (exercise / 'TASK.md').is_file() and (exercise / 'tests' / 'test_lesson.py').is_file(), lesson['root']
        for path in exercise.rglob('*.py'):
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            python_files += 1
        archived = set()
        with ZipFile(ROOT / 'downloads' / (lesson['root'] + '.zip')) as package:
            assert package.testzip() is None, lesson['root']
            for name in package.namelist():
                relative = Path(*Path(name).parts[1:]).as_posix()
                archived.add(relative)
                assert normalized(package.read(name), name) == normalized((exercise / relative).read_bytes(), name), \
                    (lesson['root'], relative, 'the archive and the exercises folder differ')
        unpacked = {path.relative_to(exercise).as_posix() for path in exercise.rglob('*') if path.is_file()
                    and '__pycache__' not in path.parts}
        assert unpacked == archived, (lesson['root'], 'extra or missing files', unpacked ^ archived)
        lines = [line for group in lesson['requirements'] for line in config['requirements'][group]]
        assert (exercise / 'requirements.txt').read_text(encoding='utf-8').split() == ' '.join(lines).split()
        if not lesson.get('own_runtime'):
            assert (exercise / 'local_llm.py').read_bytes() == runtime, (lesson['root'], 'local_llm.py differs')
        else:
            # In lesson 1 the module has a stub: the reference solution must restore the shared module byte for byte.
            stub = (exercise / 'local_llm.py').read_text(encoding='utf-8')
            assert solved_file(lesson['root'], 'local_llm.py', stub).encode('utf-8') == runtime, lesson['root']
        for file, name in lesson['targets']:
            assert name.split('.')[-1] in (exercise / file).read_text(encoding='utf-8'), (lesson['root'], file, name)
        demo_source = (exercise / 'demo.py').read_text(encoding='utf-8')
        assert 'Example' not in demo_source, (lesson['root'], 'demo.py must work with the real model')
        # A copy in .checks: the check creates no files in the exercise folder.
        with tempfile.TemporaryDirectory(prefix=lesson['root'] + '-', dir=scratch) as folder:
            copy = Path(folder) / lesson['root']
            shutil.copytree(exercise, copy)
            for module in ('demo_check', 'demo'):
                output = run(copy, module)
                assert 'Complete' in output, (lesson['root'], module, output)
        print(lesson['root'] + ': archive, starter and unfinished demos are in order')
    shutil.rmtree(scratch, ignore_errors=True)
    print(f'Checked: {pages} pages, {links} local links, {text_files} text files without Cyrillic, '
          f'{python_files} Python files, {len(config["lessons"])} starters. No models were loaded and no network was used.')
    subprocess.run([sys.executable, '-B', str(ROOT / 'tools' / 'test_model_runtime.py')], check=True)


if __name__ == '__main__':
    main()
