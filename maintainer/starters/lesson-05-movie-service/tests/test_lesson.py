import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from demo_check import ExampleEmbedder
from repository import MovieRepository
from search import KeywordSearch, SemanticSearch
from service import CatalogService


class LessonTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.repository = MovieRepository(Path(self.folder.name) / 'test.db')

    def tearDown(self):
        self.folder.cleanup()

    def test_semantic_search_in_service(self):
        service = CatalogService(self.repository, SemanticSearch(ExampleEmbedder()))
        service.load_seed(ROOT / 'data' / 'movies.json')
        self.assertEqual(service.find('hockey movie', top=1)[0]['title'], 'Miracle')
        self.assertEqual(len(service.find('space', top=2)), 2)

    def test_vectors_cached(self):
        model = ExampleEmbedder()
        search = SemanticSearch(model)
        movies = [{'id': 7, 'title': 'A', 'description': 'about the war'}]
        search.find('war', movies)
        search.find('space', movies)
        self.assertEqual(len(model.calls), 3)

    def test_service_accepts_any_search(self):
        service = CatalogService(self.repository, KeywordSearch())
        service.add_movie('Test', 2000, 'A film about hockey', ['sports'])
        self.assertEqual(service.find('hockey')[0]['title'], 'Test')


if __name__ == '__main__':
    unittest.main()
