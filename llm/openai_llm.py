from openai import OpenAI
from openai.types.chat import ChatCompletionMessageFunctionToolCall 
import logging
import time

class OpenAILLM():
    def __init__(self, api_key, base_url, model_name, tools=[]):
        self.model_name = model_name
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.tools = tools

    def generate(self, prompt: str) -> str | ChatCompletionMessageFunctionToolCall:
        start_time = time.time()

        # This is the old API, because some models (like big-pickle) do not support the new one
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            tools=self.tools,
            tool_choice="auto"
        )

        elapsed_time = time.time() - start_time
        self.log_response_stats(elapsed_time, response)

        
        if response.choices[0].finish_reason == "tool_calls":
            return response.choices[0].message.tool_calls[0]

        return response.choices[0].message.content
    
    def log_response_stats(self, response_time, response):
        prompt_tokens = response.usage.prompt_tokens
        reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens if response.usage.completion_tokens_details else None 
        answer_tokens = response.usage.completion_tokens - (reasoning_tokens if reasoning_tokens else 0)

        generation_speed = ((reasoning_tokens if reasoning_tokens else 0) + answer_tokens) / response_time if response_time > 0 else 0

        logger = logging.getLogger(f"refactoring.{__name__}")
        logger.debug(f"{type(self).__name__}: prompt_tokens={prompt_tokens}{", reasoning_tokens={reasoning_tokens}}" if reasoning_tokens else ''}, answer_tokens={answer_tokens}, time={response_time:.2f}, generation_speed={generation_speed:.2f} tokens/second")