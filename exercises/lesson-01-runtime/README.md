# The model inside the program

The first lesson of stage 2. Here the model is loaded straight into a Python program
through llama-cpp-python, with no Ollama and no cloud service.

1. Open this folder in PyCharm with File -> Open.
2. Choose the shared course interpreter (the lesson explains how to create it) and install the dependencies:

```powershell
python -m pip install --only-binary=:all: -r requirements.txt
```

3. Run check_install.py, then get_models.py: the model is downloaded into the shared course folder.
4. Complete ask in local_llm.py using TASK.md.
5. Run demo_check.py: it needs no real model.
6. Run demo.py: the model's answer appears in the Run panel at the bottom.

Once ask is done, demo_check.py prints:

```text
Offline check: You can return an item within 14 days.
```

Checks: tests/test_lesson.py -> class LessonTests -> Run.
