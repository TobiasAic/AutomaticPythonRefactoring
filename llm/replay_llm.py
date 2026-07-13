from llm.openai_llm import OpenAILLM
from llm.llm_types import LLMResponse, OpenAILLMConfig
from enum import Enum
import json
import hashlib

class ReplayMode(Enum):
    RECORD = "record"
    REPLAY = "replay"

class ReplayLLM(OpenAILLM):
    def __init__(self, config: OpenAILLMConfig, filepath: str, mode: ReplayMode = ReplayMode.REPLAY):
        super().__init__(config)
        self.prompt_responses = HashDictionary()
        self.mode = mode
        self.filepath = filepath
        if self.mode == ReplayMode.REPLAY:
            self.load_prompt_responses()

    def generate(self, prompt: str, tools: list[dict] = []) -> LLMResponse:
        if self.mode == ReplayMode.REPLAY:
            return self.replay_response(prompt)
        else:
            return self.generate_new_and_record(prompt, tools)
        
    def batch_generate(self, prompts: list[str], tools: list[list[dict]] = None) -> list[LLMResponse]:
        if tools is None:
            tools = [[] for _ in prompts]
        elif len(tools) != len(prompts):
            raise ValueError("Length of tools list must match length of prompts list.")
        
        if self.mode == ReplayMode.REPLAY:
            responses = []
            for prompt in prompts:
                responses.append(self.replay_response(prompt))
            return responses
        else:
            responses = super().batch_generate(prompts, tools)
            for prompt, response in zip(prompts, responses):
                self.prompt_responses[prompt] = response
            self.save_prompt_responses()
            return responses
        
    def replay_response(self, prompt: str) -> LLMResponse:
        response = self.prompt_responses[prompt]
        if response is None:
            raise ValueError(f"No response found for prompt: {prompt}")
        return response

    def generate_new_and_record(self, prompt: str, tools: list[dict] = []) -> LLMResponse:
        response = super().generate(prompt, tools)
        self.prompt_responses[prompt] = response
        self.save_prompt_responses()
        return response
    
    def save_prompt_responses(self):
        with open(self.filepath, "w") as f:
            json.dump({prompt: response.to_dict() for prompt, response in self.prompt_responses.items()}, f, indent=4)

    def load_prompt_responses(self):
        with open(self.filepath, "r") as f:
            self.prompt_responses = HashDictionary({prompt: LLMResponse.from_dict(response_data) for prompt, response_data in json.load(f).items()})


class HashDictionary:
    def __init__(self, data = {}):
        self.data = data

    def __setitem__(self, key, value):
        hashed_key = self.hash_key(key)
        self.data[hashed_key] = value

    def __getitem__(self, key):
        hashed_key = self.hash_key(key)
        return self.data[hashed_key]

    def __contains__(self, key):
        hashed_key = self.hash_key(key)
        return hashed_key in self.data
    
    def items(self):
        return self.data.items()

    def hash_key(self, key):
        if isinstance(key, str):
            return hashlib.sha256(key.encode()).hexdigest()
        else:
            raise TypeError("Keys must be strings.")