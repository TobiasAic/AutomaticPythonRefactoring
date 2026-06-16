from llm.openai_llm import OpenAILLM
from llm.llm_types import LLMResponse, OpenAILLMConfig
from enum import Enum
import json

class ReplayMode(Enum):
    RECORD = "record"
    REPLAY = "replay"

class ReplayLLM(OpenAILLM):
    def __init__(self, config: OpenAILLMConfig, tools: list[dict] = [], mode: ReplayMode = ReplayMode.REPLAY):
        super().__init__(config, tools)
        self.responses = []
        self.mode = mode

    def generate(self, prompt: str) -> LLMResponse:
        if self.mode == ReplayMode.REPLAY:
            return self.replay_last_response()
        else:
            return self.generate_new_and_record(prompt) 
        
    def replay_last_response(self) -> LLMResponse:
        if not self.responses:
            raise ValueError("No responses to replay")
        return self.responses.pop(0)
    
    def generate_new_and_record(self, prompt: str) -> LLMResponse:
        response = super().generate(prompt)
        self.responses.append(response)
        return response
    
    def save_responses(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump([response.to_dict() for response in self.responses], f, indent=4)

    def load_responses(self, filepath: str):
        with open(filepath, "r") as f:
            self.responses = [LLMResponse.from_dict(response_data) for response_data in json.load(f)]