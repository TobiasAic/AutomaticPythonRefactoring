from openai import OpenAI
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from llm.llm import LLM
from llm.llm_types import OpenAILLMConfig, LLMResponse, ToolCall
from utility.cli import CLI

class OpenAILLM(LLM):
    def __init__(self, config: OpenAILLMConfig):
        self.model_name = config.model_name
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=1800
        )

    def generate(self, prompt: str, tools: list[dict] = []) -> LLMResponse:
        start_time = time.time()

        # This is the old API, because some models (like big-pickle) do not support the new one
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice="auto"
        )

        elapsed_time = time.time() - start_time
        self.log_response_stats(elapsed_time, response)

        
        if response.choices[0].finish_reason == "tool_calls":
            return LLMResponse(
                text=None,
                tool_call=ToolCall(
                    name=response.choices[0].message.tool_calls[0].function.name,
                    arguments=response.choices[0].message.tool_calls[0].function.arguments
                )
            )

        return LLMResponse(
            text=response.choices[0].message.content,
            tool_call=None
        )
    
    def batch_generate(self, prompts: list[str], tools: list[list[dict]] = None) -> list[LLMResponse]:
        if tools is None:
            tools = [[] for _ in prompts]
        elif len(tools) != len(prompts):
            raise ValueError("Length of tools list must match length of prompts list.")

        llm_responses = [None] * len(prompts)
        with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
            futures = {
                executor.submit(self.generate, prompt, tool): index
                for index, (prompt, tool) in enumerate(zip(prompts, tools))
            }

            with tqdm(total=len(prompts), desc="LLM Responses", unit="responses") as progress_bar:
                for future in as_completed(futures):
                    index = futures[future]
                    llm_responses[index] = future.result()
                    progress_bar.update(1)
        
        return llm_responses

    def log_response_stats(self, response_time, response):
        prompt_tokens = response.usage.prompt_tokens
        reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens if response.usage.completion_tokens_details else None 
        answer_tokens = response.usage.completion_tokens - (reasoning_tokens if reasoning_tokens else 0)

        generation_speed = ((reasoning_tokens if reasoning_tokens else 0) + answer_tokens) / response_time if response_time > 0 else 0

        CLI.print_debug(f"{type(self).__name__}: prompt_tokens={prompt_tokens}{", reasoning_tokens={reasoning_tokens}}" if reasoning_tokens else ''}, answer_tokens={answer_tokens}, time={response_time:.2f}, generation_speed={generation_speed:.2f} tokens/second")