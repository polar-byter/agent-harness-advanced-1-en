# Hints for lesson 5. The model in a web service

> **Where we are.** A home movie catalog already runs in the browser and searches by words. We add search by meaning with an embedding model, without rewriting the rest of the service. Today we write `SemanticSearch.find` and connect it in `run.py`.
> **From the main course:** `find_notes` as the retrieval step before the answer; `send_live` as one entry point to different model services.
> **New:** embeddings and cosine similarity, a service split into layers, a strategy, an adapter, dependency injection and a composition point.
> `browser -> web.py -> CatalogService -> search -> [SemanticSearch: query -> vector -> closeness] -> movies -> page`

Current task: `search.py` -> `SemanticSearch.find`, `run.py` -> `main`. The full lesson: course/05-movie-service.md in the course repository.

## Your turn

Open `search.py`. `SemanticSearch` already has `vector`, which turns text into a vector of length 1, and `movie_vector`, a movie's vector. `movie_vector` keeps computed vectors in the `self.vectors` dictionary by movie id, so the model processes each movie once rather than on every search. The `cosine` function at the top of the file computes the closeness of two vectors of length 1: the sum of pairwise products.

Replace the line `raise NotImplementedError(...)` in `find` with the fragment below and fill in the three gaps:

```python
        query_vector = self.vector(self.TASK + ...)
        scored = []
        for movie in movies:
            scored.append((cosine(query_vector, self.movie_vector(...)), movie))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [movie for score, movie in scored[:...]]
```

1. After `self.TASK +` put `query`. `TASK` is the task explanation for Qwen3-Embedding discussed above.
2. Pass `movie` to `self.movie_vector(...)`.
3. Put `top` in the slice.

The indent here is eight spaces: the code is inside a method, and the method is inside a class. The loop puts `(closeness, movie)` pairs into the `scored` list. `sort` with `key=lambda pair: pair[0]` sorts the pairs by their first element, the closeness, and `reverse=True` puts the closest first. Without `key`, Python would try to compare the movie dictionaries themselves when closeness is equal and raise an error. The service needs only the movies, so the last line takes the movie from the first `top` pairs and drops the closeness number.

## Connect the search

Open `run.py`. Right now `main` builds the service with the word search:

```python
def main():
    serve(build_service(KeywordSearch()))
```

Replace its body so the service gets the embedding model:

```python
def main():
    with load_embedder() as model:
        serve(build_service(SemanticSearch(...)))
```

Pass `model` to `SemanticSearch(...)`. The `with` block keeps the model loaded while the server runs and frees the memory after **Stop**. The server starts with `threaded=False`: requests are handled one at a time, and the model never gets two calls at once. That is enough for a home catalog; serving many users at once is decided at a real deployment.

## Guess before running

What will the word search find, and what will the search by meaning find, for the query "a gentle cartoon before bed"?

## Run it

Open `demo_check.py` and choose **Run 'demo_check'**. The stand-in model builds vectors from preselected words. The check searches a small list of movies, makes sure movie vectors are taken through `movie_vector` and goes the whole path through the web layer on a temporary database. Once the search is done:

```text
Offline check: time travel -> Back to the Future
```

Now **Run 'demo'**: it compares the two searches on four queries without starting the server. When the course was prepared:

```text
time travel
  by words:   ['Back to the Future']
  by meaning: ['Back to the Future', 'Galaxy Quest', 'WALL-E']
hockey movie
  by words:   []
  by meaning: ['Miracle', 'The Snowman', 'Galaxy Quest']
a gentle cartoon before bed
  by words:   []
  by meaning: ['The Snowman', 'WALL-E', 'Groundhog Day']
```

The first movie in the search by meaning was correct in all four queries, and the second and third are simply the closest of the rest. There are ten movies in the catalog, and the search always returns the three best, even if only one fits.

Finally, **Run 'run'** again and open http://127.0.0.1:5000. Use the form to add the movie "Tom and Jerry" with the description "A cat chases a mouse around the house and keeps getting into funny trouble" and search for "cat and mouse". When the course was prepared, the new movie came first: its vector was computed on the first search and remembered.

## Try to break it

**Bring back the old strategy.** In `run.py` replace `SemanticSearch(model)` with `KeywordSearch()`, keeping the `with` block. The service starts, the page and the form work as before, only the search changes. Neither `web.py` nor `service.py` had to be touched. Put the search by meaning back.

**Bypass the vector store.** In `find`, write `self.vector(movie['title'] + '. ' + movie['description'])` instead of `self.movie_vector(movie)` and run `demo_check.py`. The check reports that movie vectors must be taken through `movie_vector`: without storing them, the model would recompute the whole catalog on every query. On ten movies you would not notice; on tens of thousands every search would wait a noticeable time. Put `movie_vector` back.

**Look at the service through a program's eyes.** Open http://127.0.0.1:5000/api/search?q=hockey%20movie. The same search returns JSON instead of a page: the web layer shows the service's result in two forms, while the search rules stay the same.
