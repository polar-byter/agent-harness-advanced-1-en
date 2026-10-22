# A vision model checks the photo from a claim

The Qwen3-VL model receives a photo and the name of the ordered item, and the program uses its answer
to decide where to send the return claim. A staff member still refunds the money.

1. Open this folder in PyCharm with File -> Open and choose the shared course interpreter.
2. Install the dependencies: `python -m pip install --only-binary=:all: -r requirements.txt`.
3. Run get_models.py: it downloads the two files of the vision model, about 1.6 GB in total.
4. Complete check_photo in photo_check.py using TASK.md.
5. Run demo_check.py, then demo.py. The model takes several seconds or more for each photo.

Once check_photo is done, demo_check.py prints:

```text
Offline check: to staff: damage is visible in the photo
```

Checks: tests/test_lesson.py -> class LessonTests -> Run. The photo sources are in data/photos/SOURCES.md.
