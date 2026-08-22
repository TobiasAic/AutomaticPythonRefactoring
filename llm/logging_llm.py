import time

from llm.llm import LLM
from utility.cli import CLI


class LoggingLLM:
    def __init__(self, llm: LLM):
        self._llm = llm

    def generate(self, *args, **kwargs):
        start_time = time.time()
        result = self._llm.generate(*args, **kwargs)
        elapsed_time = time.time() - start_time
        CLI.print_debug(f"Generated response in {elapsed_time:.2f} seconds")
        return result

    def __getattr__(self, name):
        # Delegate everything else to the wrapped LLM.
        return getattr(self._llm, name)
