"""Downloads this lesson's models into the shared course models folder."""
import sys

from local_llm import download, models_dir

MODELS = ['embed']


def main():
    print('Models folder:', models_dir())
    # Run with the parameter small downloads the small language model instead of the main one.
    small = 'small' in sys.argv[1:]
    download(*[('chat-small' if small and name == 'chat' else name) for name in MODELS])


if __name__ == '__main__':
    main()
