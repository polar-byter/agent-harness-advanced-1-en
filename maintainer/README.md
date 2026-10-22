# Course maintenance

Lesson texts live in `course`, starter code and reference solutions in `maintainer`. Diagrams are drawn by a script in `tools`.

```text
maintainer/starters/<lesson>     starter sources without the shared files
maintainer/solutions/<lesson>    reference solutions, never given to the reader
maintainer/make_data.py          rebuilds the Excel journals; with "voice" it also synthesizes call.wav
tools/model_runtime/local_llm.py the shared module, copied into the starters
tools/course-map.json            lessons, models, dependencies, expected output
tools/course_flow_examples.py    data for the lesson diagrams
```

## Update the course

In the repository root, in an environment with the course dependencies and Pillow:

```powershell
python tools/draw_course_flows.py
python tools/build_starters.py
python tools/check_course.py
python tools/check_solutions.py
```

`draw_course_flows.py` draws GIFs and static PNGs 480 pixels wide into `assets`. `build_starters.py` assembles each starter: the sources, `local_llm.py`, `get_models.py`, `requirements.txt`, `.gitignore` and `TASK.md`, which is built from the lesson sections ("Where we are", "Your turn", "Connect", "Guess before running", "Run it", "Try to break it"). It unpacks each starter into `exercises` and writes a ZIP with a fixed file date into `downloads`.

## What is checked

`check_course.py` checks punctuation and links in Markdown, the absence of Cyrillic text, Python syntax, that every ZIP matches its `exercises` folder, the contents of `requirements.txt`, that `local_llm.py` matches the shared module, and that the unfinished `demo_check.py` and `demo.py` print the `Complete` hint. No models or network are used.

`check_solutions.py` substitutes the reference solutions in temporary copies, runs `tests/test_lesson.py` and `demo_check.py` and compares the output with the `expected` field of the course map. This checks the starters and tests, not model quality.

Runs on real models are done by hand: download the models into a folder outside the repository, set `AGENT_MODELS_DIR` and run `demo.py` in copies with the solutions applied. Record the results in `WORK_LOG.md`, and quote in lessons only results from such runs.
