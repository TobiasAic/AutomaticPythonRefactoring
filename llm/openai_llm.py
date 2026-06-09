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
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        elapsed_time = time.time() - start_time
        self.log_response_stats(elapsed_time, response)
        return response.choices[0].message.content
    
    def log_response_stats(self, response_time, response):
        prompt_tokens = response.usage.prompt_tokens
        reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens
        answer_tokens = response.usage.completion_tokens - reasoning_tokens

        generation_speed = (reasoning_tokens + answer_tokens) / response_time if response_time > 0 else 0

        logger = logging.getLogger(f"refactoring.{__name__}")
        logger.debug(f"{type(self).__name__}: prompt_tokens={prompt_tokens}, reasoning_tokens={reasoning_tokens}, answer_tokens={answer_tokens}, generation_speed={generation_speed:.2f} tokens/second")