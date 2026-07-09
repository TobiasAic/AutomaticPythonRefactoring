from typing import override

from openai import OpenAI
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from llm.llm import LLM
from llm.llm_types import OpenAILLMConfig, LLMResponse, ToolCall

class OllamaLLM(LLM):
    def __init__(self, configs: list[OpenAILLMConfig]):
        self.model_name = configs[0].model_name
        for i in range(1, len(configs)):
            if configs[i].model_name != self.model_name:
                raise ValueError("All configs must have the same model_name.")
            
        self.clients = [OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=1800
        ) for config in configs]

    @override
    def generate(self, client, prompt: str, tools: list[dict] = []) -> LLMResponse:
        start_time = time.time()

        # This is the old API, because some models (like big-pickle) do not support the new one
        response = client.chat.completions.create(
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

    @override 
    def batch_generate(self, prompts: list[str], tools: list[list[dict]] = None) -> list[LLMResponse]:
        if tools is None:
            tools = [[] for _ in prompts]
        elif len(tools) != len(prompts):
            raise ValueError("Length of tools list must match length of prompts list.")

        if not prompts:
            return []

        if not self.clients:
            raise ValueError("At least one Ollama client is required.")

        llm_responses = [None] * len(prompts)

        client_batches: list[list[tuple[int, str, list[dict]]]] = [[] for _ in self.clients]
        for index, (prompt, tool) in enumerate(zip(prompts, tools)):
            client_batches[index % len(self.clients)].append((index, prompt, tool))

        def process_batch(client, batch: list[tuple[int, str, list[dict]]]) -> None:
            for index, prompt, tool in batch:
                llm_responses[index] = self.generate(client, prompt, tool)

        with ThreadPoolExecutor(max_workers=len(self.clients)) as executor:
            futures = [
                executor.submit(process_batch, client, batch)
                for client, batch in zip(self.clients, client_batches)
                if batch
            ]

            with tqdm(total=len(prompts), desc="LLM Responses", unit="responses") as progress_bar:
                for future in as_completed(futures):
                    future.result()
                    progress_bar.update(1)
        
        return llm_responses