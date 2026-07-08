from llm.openai_llm import OpenAILLM
from llm.llm_types import LLMResponse, OpenAILLMConfig
from enum import Enum
import json

class ReplayMode(Enum):
    RECORD = "record"
    REPLAY = "replay"

class ReplayLLM(OpenAILLM):
    def __init__(self, config: OpenAILLMConfig, filepath: str, mode: ReplayMode = ReplayMode.REPLAY):
        super().__init__(config)
        self.responses = []
        self.mode = mode
        self.filepath = filepath
        if self.mode == ReplayMode.REPLAY:
            self.load_responses()

    def generate(self, prompt: str, tools: list[dict] = []) -> LLMResponse:
        if self.mode == ReplayMode.REPLAY:
            return self.replay_last_response()
        else:
            return self.generate_new_and_record(prompt, tools)
        
    def batch_generate(self, prompts: list[str], tools: list[list[dict]] = None) -> list[LLMResponse]:
        raise NotImplementedError("Batch generation is not supported in ReplayLLM. Use generate() for individual prompts.")
        
    def replay_last_response(self) -> LLMResponse:
        if not self.responses:
            raise ValueError("No responses to replay")
        return self.responses.pop(0)
    
    def generate_new_and_record(self, prompt: str, tools: list[dict] = []) -> LLMResponse:
        response = super().generate(prompt, tools)
        self.responses.append(response)
        self.save_responses()
        return response
    
    def save_responses(self):
        with open(self.filepath, "w") as f:
            json.dump([response.to_dict() for response in self.responses], f, indent=4)

    def load_responses(self):
        with open(self.filepath, "r") as f:
            self.responses = [LLMResponse.from_dict(response_data) for response_data in json.load(f)]