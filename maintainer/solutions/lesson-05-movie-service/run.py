"""The composition point: here we choose the storage and the search method and start the service."""
from pathlib import Path

from local_llm import load_embedder
from repository import MovieRepository
from search import KeywordSearch, SemanticSearch
from service import CatalogService
from web import create_app

ROOT = Path(__file__).resolve().parent


def build_service(search) -> CatalogService:
    service = CatalogService(MovieRepository(ROOT / 'data' / 'movies.db'), search)
    service.load_seed(ROOT / 'data' / 'movies.json')
    return service


def serve(service: CatalogService) -> None:
    print('Catalog is open: http://127.0.0.1:5000')
    # One model answers one request at a time, so the server runs in a single thread.
    create_app(service).run(host='127.0.0.1', port=5000, threaded=False)


def main():
    with load_embedder() as model:
        serve(build_service(SemanticSearch(model)))


if __name__ == '__main__':
    main()
