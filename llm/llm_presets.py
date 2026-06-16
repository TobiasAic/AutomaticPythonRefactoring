from llm.openai_llm import OpenAILLMConfig
from utility.enviroment_variables import get_env_variable

big_pickle_config = OpenAILLMConfig(
    api_key=get_env_variable("OPENCODE_API_KEY"),
    base_url="https://opencode.ai/zen/v1",
    model_name="big-pickle"
)

qwen3_5_2b_config = OpenAILLMConfig(
    api_key="supersecret", # dummy value, Ollama does not require an API key
    base_url="http://localhost:11434/v1",
    model_name="qwen3.5:2b"
)