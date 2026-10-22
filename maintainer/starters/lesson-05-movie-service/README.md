# Movie catalog: the model in a web service

A ready local Flask service: a list of movies, a tag filter, search and a form to add a movie.
The task is to bring search by meaning into it, using the Qwen3-Embedding model.

```text
web.py         web layer: addresses and pages
service.py     catalog rules: CatalogService
repository.py  storage in SQLite: MovieRepository
search.py      search methods: KeywordSearch and SemanticSearch
run.py         composition point: what to connect and start
```

1. Open this folder in PyCharm with File -> Open and choose the shared course interpreter.
2. Install the dependencies: `python -m pip install --only-binary=:all: -r requirements.txt`.
3. Run get_models.py: it downloads the embedding model, about 640 MB.
4. Run run.py and open http://127.0.0.1:5000 in a browser. To stop the server, press the red Stop square in Run.
5. Complete SemanticSearch.find in search.py and connect it in run.py using TASK.md.
6. Run demo_check.py, then demo.py and run.py again.

Once the search is done, demo_check.py prints:

```text
Offline check: time travel -> Back to the Future
```

Checks: tests/test_lesson.py -> class LessonTests -> Run.
