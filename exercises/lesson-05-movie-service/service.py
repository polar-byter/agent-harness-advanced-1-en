"""The catalog rules layer. The service knows nothing about HTTP, SQLite or a particular model."""
import json
from pathlib import Path


class CatalogService:
    def __init__(self, repository, search):
        # Dependencies are passed in from outside: that makes them easy to replace in tests and at startup.
        self.repository = repository
        self.search = search

    def add_movie(self, title: str, year: int, description: str, tags: list[str]) -> int:
        title, description = title.strip(), description.strip()
        if not title or not description:
            raise ValueError('A title and a description are required')
        tags = sorted({tag.strip().casefold() for tag in tags if tag.strip()})
        return self.repository.add(title, year, description, tags)

    def movies(self, tag: str | None = None) -> list[dict]:
        movies = self.repository.list_all()
        return [movie for movie in movies if tag in movie['tags']] if tag else movies

    def find(self, query: str, top: int = 3) -> list[dict]:
        if not query.strip():
            return []
        return self.search.find(query.strip(), self.repository.list_all(), top)

    def all_tags(self) -> list[str]:
        return sorted({tag for movie in self.repository.list_all() for tag in movie['tags']})

    def load_seed(self, path: Path) -> None:
        """First run: fill the empty catalog with movies from JSON."""
        if self.repository.count():
            return
        for movie in json.loads(path.read_text(encoding='utf-8')):
            self.repository.add(movie['title'], movie['year'], movie['description'], movie['tags'])
