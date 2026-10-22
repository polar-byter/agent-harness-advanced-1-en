import sys

from local_llm import models_dir, chat_model_name, model_path


def main():
    print('Python:', sys.version.split()[0])
    print('Interpreter:', sys.executable)
    try:
        import llama_cpp
    except (ImportError, OSError) as error:
        print('The library did not load yet:', error)
        return
    print('Library loaded:', llama_cpp.__version__)
    print('Models folder:', models_dir())
    path = model_path(chat_model_name())
    print('Model file:', path.name, '- found' if path.is_file() else '- not downloaded yet')


if __name__ == '__main__':
    main()
