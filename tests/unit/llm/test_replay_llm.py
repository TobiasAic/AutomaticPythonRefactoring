from llm.llm_types import LLMResponse, OpenAILLMConfig
from llm.replay_llm import ReplayLLM, ReplayMode


def test_replay_llm_records_saves_loads_and_replays(tmp_path, monkeypatch):
    expected_response = LLMResponse(text="hello")

    def fake_generate(self, prompt, tools):
        return expected_response

    monkeypatch.setattr("llm.openai_llm.OpenAILLM.generate", fake_generate)

    config = OpenAILLMConfig(api_key="test-key", base_url="http://localhost", model_name="test-model")
    responses_file = tmp_path / "responses.json"

    recording_llm = ReplayLLM(config, responses_file, mode=ReplayMode.RECORD)
    assert recording_llm.generate("ignored prompt") == expected_response
    assert recording_llm.responses == [expected_response]
    
    replay_llm = ReplayLLM(config, responses_file, mode=ReplayMode.REPLAY)

    assert replay_llm.generate("another ignored prompt") == expected_response
    assert replay_llm.responses == []