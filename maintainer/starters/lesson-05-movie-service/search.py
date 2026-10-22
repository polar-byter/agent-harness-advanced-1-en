"""Ways to search for movies. Both have one find method, so the service can take either."""
import math


def cosine(a: list[float], b: list[float]) -> float:
    """For vectors of length 1, cosine similarity is the sum of pairwise products."""
    return sum(x * y for x, y in zip(a, b))


class KeywordSearch:
    """The old way: a movie fits if its title or description contains a word from the query."""

    def find(self, query: str, movies: list[dict], top: int = 3) -> list[dict]:
        words = [word for word in query.casefold().split() if len(word) > 3]
        found = [movie for movie in movies
                 if any(word in (movie['title'] + ' ' + movie['description']).casefold() for word in words)]
        return found[:top]


class SemanticSearch:
    """Search by meaning: the query and the movies become vectors, and the nearest vectors are the best movies."""
    TASK = "Instruct: Find a movie from the viewer's description\nQuery: "

    def __init__(self, model):
        self.model = model
        self.vectors = {}  # movie id -> vector; each movie is computed once

    def vector(self, text: str) -> list[float]:
        values = self.model.embed(text)
        length = math.sqrt(sum(value * value for value in values))
        return [value / length for value in values]

    def movie_vector(self, movie: dict) -> list[float]:
        if movie['id'] not in self.vectors:
            self.vectors[movie['id']] = self.vector(movie['title'] + '. ' + movie['description'])
        return self.vectors[movie['id']]

    def find(self, query: str, movies: list[dict], top: int = 3) -> list[dict]:
        # Turn the query into a vector, score its closeness to each movie and return the best movies.
        raise NotImplementedError('Complete SemanticSearch.find in search.py using the lesson 5 hints')
