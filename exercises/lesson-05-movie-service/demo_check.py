import tempfile
from pathlib import Path

from repository import MovieRepository
from search import SemanticSearch
from service import CatalogService
from web import create_app

ROOT = Path(__file__).resolve().parent
QUERY = 'time travel'


class ExampleEmbedder:
    """A stand-in for the embedding model: each vector dimension stands for one topic."""
    TOPICS = [('time', 'future'), ('space', 'planet'), ('war', 'fighter'), ('hockey', 'puck'), ('love', 'court')]

    def __init__(self):
        self.calls = []

    def embed(self, text):
        self.calls.append(text)
        lowered = text.casefold()
        return [1.0 + sum(word in lowered for word in words) * 5 for words in self.TOPICS]


def check_exercise():
    model = ExampleEmbedder()
    search = SemanticSearch(model)
    movies = [{'id': 1, 'title': 'A hockey movie', 'description': 'A match against the Soviet team.'},
              {'id': 2, 'title': 'The Time Machine', 'description': 'The hero travels to the future.'}]
    found = search.find(QUERY, movies, top=1)
    assert model.calls[0] == SemanticSearch.TASK + QUERY, 'First turn the query with the TASK explanation into a vector'
    assert found == [movies[1]], 'Return the list of movies, closest first'
    search.find('hockey', movies)
    assert len(model.calls) == 4, 'Take movie vectors through movie_vector: they are computed once'
    # Check the whole path through the web layer on a temporary database; the working catalog stays untouched.
    with tempfile.TemporaryDirectory() as folder:
        service = CatalogService(MovieRepository(Path(folder) / 'test.db'), SemanticSearch(ExampleEmbedder()))
        service.load_seed(ROOT / 'data' / 'movies.json')
        client = create_app(service).test_client()
        movie = client.get('/api/search', query_string={'q': QUERY}).get_json()['movies'][0]
    return f'{QUERY} -> {movie["title"]}'


def main():
    try:
        print('Offline check:', check_exercise())
    except NotImplementedError as error:
        print(error)


if __name__ == '__main__':
    main()
