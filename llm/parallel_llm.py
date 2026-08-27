from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

from llm.llm import LLM


class ParallelLLM:
    def __init__(self, llm: LLM):
        self._llm = llm

    def batch_generate(
        self,
        prompts: list[str],
        tools: list[list[dict]] | None = None,
        require_tool_call: bool = False,
    ):
        if tools is None:
            tools = [[] for _ in prompts]
        elif len(tools) != len(prompts):
            raise ValueError(
                "Length of tools list must match length of prompts list."
            )

        if len(prompts) > 10:
            raise ValueError(
                "Batch generation is limited to 10 prompts at a time to avoid overwhelming the LLM."
            )

        responses = [None] * len(prompts)

        with ThreadPoolExecutor(max_workers=len(prompts)) as executor:
            futures = {
                executor.submit(self._llm.generate, prompt, tool, require_tool_call=require_tool_call): i
                for i, (prompt, tool) in enumerate(zip(prompts, tools))
            }

            with tqdm(
                total=len(prompts),
                desc="LLM Responses",
                unit="responses",
            ) as progress_bar:
                for future in as_completed(futures):
                    responses[futures[future]] = future.result()
                    progress_bar.update(1)

        return responses

    def __getattr__(self, name):
        return getattr(self._llm, name)