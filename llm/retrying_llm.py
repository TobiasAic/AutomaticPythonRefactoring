import time

from llm.llm import LLM
from utility.cli import CLI


class RetryingLLM:
    def __init__(self, llm: LLM, max_retries: int = 3, delay_seconds: float = 1.0):
        self._llm = llm
        self._max_retries = max_retries
        self._delay_seconds = delay_seconds

    def generate(self, *args, **kwargs):
        last_exception = None
        for attempt in range(1, self._max_retries + 1):
            try:
                return self._llm.generate(*args, **kwargs)
            except Exception as exception:
                last_exception = exception
                CLI.print_debug(
                    f"Attempt {attempt}/{self._max_retries} to generate response failed: {exception}"
                )
                if attempt < self._max_retries:
                    time.sleep(self._delay_seconds)
        raise last_exception

    def __getattr__(self, name):
        # Delegate everything else to the wrapped LLM.
        return getattr(self._llm, name)
