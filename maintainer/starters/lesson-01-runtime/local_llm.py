"""Shared course module: where the model files live, how to download them and load them into the program.

The same file sits in every starter. Model libraries are imported inside the functions,
so the offline checks work even where llama-cpp-python is not installed yet.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import urllib.request

HF = 'https://huggingface.co/'
# Name in the program -> (file, address, approximate size in MB).
MODELS = {
    'chat': ('Qwen3-1.7B-Q8_0.gguf', HF + 'Qwen/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q8_0.gguf', 1834),
    'chat-small': ('Qwen3-0.6B-Q8_0.gguf', HF + 'Qwen/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q8_0.gguf', 639),
    'embed': ('Qwen3-Embedding-0.6B-Q8_0.gguf',
              HF + 'Qwen/Qwen3-Embedding-0.6B-GGUF/resolve/main/Qwen3-Embedding-0.6B-Q8_0.gguf', 639),
    'vision': ('Qwen3VL-2B-Instruct-Q4_K_M.gguf',
               HF + 'Qwen/Qwen3-VL-2B-Instruct-GGUF/resolve/main/Qwen3VL-2B-Instruct-Q4_K_M.gguf', 1107),
    'vision-proj': ('mmproj-Qwen3VL-2B-Instruct-Q8_0.gguf',
                    HF + 'Qwen/Qwen3-VL-2B-Instruct-GGUF/resolve/main/mmproj-Qwen3VL-2B-Instruct-Q8_0.gguf', 445),
    'speech': ('ggml-small.bin', HF + 'ggerganov/whisper.cpp/resolve/main/ggml-small.bin', 488),
}

# Token sampling settings from the Qwen3 model card for the non-thinking mode.
SAMPLING = {'temperature': 0.7, 'top_p': 0.8, 'top_k': 20, 'min_p': 0.0, 'presence_penalty': 1.5}
# Qwen3 command: answer straight away, without a long reasoning block.
NO_THINK = ' /no_think'
_quiet_log = None  # keep a reference to the log function while the vision model is running


def models_dir() -> Path:
    """One models folder per computer: files are not downloaded again for every lesson."""
    folder = os.environ.get('AGENT_MODELS_DIR')
    return Path(folder) if folder else Path.home() / 'agent-models'


def model_path(name: str) -> Path:
    return models_dir() / MODELS[name][0]


def require(name: str) -> Path:
    path = model_path(name)
    if not path.is_file():
        raise FileNotFoundError(f'Model file {path.name} is missing in {path.parent}. '
                                f"Run this lesson's get_models.py.")
    return path


def download(*names: str) -> None:
    """Download missing files. Until the download finishes, the file is named *.part."""
    folder = models_dir()
    folder.mkdir(parents=True, exist_ok=True)
    for name in names:
        filename, url, size = MODELS[name]
        target = folder / filename
        if target.is_file():
            print(f'{filename}: already downloaded')
            continue
        print(f'{filename}: downloading about {size} MB to {folder}')
        partial = target.with_name(filename + '.part')

        def progress(blocks, block_size, total):
            if total > 0 and blocks % 2000 == 0:
                print(f'  {min(100, blocks * block_size * 100 // total)}%')

        urllib.request.urlretrieve(url, partial, progress)
        partial.replace(target)
        print(f'{filename}: done')


def chat_model_name() -> str:
    """Use the main model, or the small one if only that one is downloaded."""
    if model_path('chat').is_file() or not model_path('chat-small').is_file():
        return 'chat'
    return 'chat-small'


@contextmanager
def load_chat(name: str | None = None, n_ctx: int = 4096):
    name = name or chat_model_name()
    path = require(name)
    from llama_cpp import Llama
    print(f'Loading {path.name}...')
    model = Llama(model_path=str(path), n_ctx=n_ctx, n_gpu_layers=0, seed=42, verbose=False)
    try:
        yield model
    finally:
        # This version of Llama does not support with, so we free the memory ourselves.
        model.close()


@contextmanager
def load_embedder():
    path = require('embed')
    from llama_cpp import Llama
    print(f'Loading {path.name}...')
    model = Llama(model_path=str(path), embedding=True, n_ctx=512, n_gpu_layers=0, verbose=False)
    try:
        yield model
    finally:
        model.close()


@contextmanager
def load_vision():
    path, projector = require('vision'), require('vision-proj')
    import llama_cpp
    import llama_cpp.mtmd_cpp as mtmd
    from llama_cpp import Llama
    from llama_cpp.llama_chat_format import MTMDChatHandler
    global _quiet_log
    # The image handler prints a detailed log even with verbose=False; switch it off.
    _quiet_log = llama_cpp.llama_log_callback(lambda level, text, data: None)
    mtmd.mtmd_log_set(_quiet_log, None)
    mtmd.mtmd_helper_log_set(_quiet_log, None)
    print(f'Loading {path.name} and {projector.name}...')
    # The projector turns the image into vectors the language part of the model understands.
    handler = MTMDChatHandler(clip_model_path=str(projector), verbose=False, use_gpu=False)
    model = Llama(model_path=str(path), chat_handler=handler, n_ctx=4096, n_gpu_layers=0, verbose=False)
    try:
        yield model
    finally:
        model.close()


@contextmanager
def load_speech():
    path = require('speech')
    from pywhispercpp.model import Model
    print(f'Loading {path.name}...')
    yield Model(str(path), redirect_whispercpp_logs_to=None, print_progress=False,
                n_threads=min(8, os.cpu_count() or 4))


def clean_answer(response: dict) -> str:
    """Take the text out of a create_chat_completion response and check that generation finished."""
    choice = response['choices'][0]
    if choice.get('finish_reason') != 'stop':
        raise ValueError('Generation did not finish: the model hit the max_tokens limit')
    text = choice['message'].get('content')
    if not isinstance(text, str):
        raise ValueError('The model returned no text')
    # Qwen3 may put an empty service block before the answer.
    text = re.sub(r'\A\s*<think>.*?</think>\s*', '', text, flags=re.S).strip()
    if not text:
        raise ValueError('The model returned an empty answer')
    return text


def ask(model, instruction: str, text: str, schema: dict | None = None, max_tokens: int = 256):
    """One request to the language model: a rule, the data and, if needed, a JSON schema."""
    settings = dict(SAMPLING, max_tokens=max_tokens)
    if schema is not None:
        # The schema restricts token choice: the model can only write JSON of this shape.
        settings['response_format'] = {'type': 'json_object', 'schema': schema}
    # Build the messages, call the model and return the text or a dictionary.
    raise NotImplementedError('Complete ask in local_llm.py using the lesson 1 hints')
