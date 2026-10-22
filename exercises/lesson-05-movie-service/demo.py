import json
from pathlib import Path

from demo_check import check_exercise
from local_llm import load_embedder
from search import KeywordSearch, SemanticSearch

ROOT = Path(__file__).resolve().parent
QUERIES = ['time travel', 'hockey movie', 'something funny about love at work', 'a gentle cartoon before bed']


def main():
    try:
        check_exercise()
        movies = json.loads((ROOT / 'data' / 'movies.json').read_text(encoding='utf-8'))
        for number, movie in enumerate(movies, start=1):
            movie['id'] = number
        keywords = KeywordSearch()
        with load_embedder() as model:
            semantic = SemanticSearch(model)
            for query in QUERIES:
                print(query)
                print('  by words:  ', [movie['title'] for movie in keywords.find(query, movies)])
                print('  by meaning:', [movie['title'] for movie in semantic.find(query, movies)])
    except (NotImplementedError, FileNotFoundError, ModuleNotFoundError, ValueError) as error:
        print(error)


if __name__ == '__main__':
    main()
