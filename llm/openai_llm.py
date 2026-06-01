from openai import OpenAI
import logging
import time

from llm.llm import LLM


class OpenAILLM(LLM):
    def __init__(self, api_key, base_url, model_name):
        self.model_name = model_name
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def generate(self, prompt: str) -> str:
        start_time = time.time()
        logger = logging.getLogger(f"refactoring.{__name__}")
        logger.debug(f"Sending prompt to OpenAI LLM: {prompt[:100]}...")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        elapsed_time = time.time() - start_time
        speed = response.usage.total_tokens / elapsed_time if elapsed_time > 0 else 0
        logger.debug(f"Received response of length {len(response.choices[0].message.content)} with speed {speed:.2f} tokens/second from OpenAI LLM: {response.choices[0].message.content[:100]}")
        return response.choices[0].message.content