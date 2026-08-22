""" Commonly used LLM configurations for convenience. """

from llm.openai_llm import LLMConfig
from utility.environment_variables import get_env_variable

big_pickle_config = LLMConfig(
    api_key=get_env_variable("OPENCODE_API_KEY"),
    base_url="https://opencode.ai/zen/v1",
    model_name="big-pickle"
)

qwen3_5_2b_config = LLMConfig(
    api_key="supersecret", # dummy value, Ollama does not require an API key
    base_url="http://localhost:11434/v1",
    model_name="qwen3.5:2b"
)

qwen3_6_35b_config = LLMConfig(
    api_key="supersecret", # dummy value, Ollama does not require an API key
    base_url="http://localhost:11434/v1",
    model_name="qwen3.6:35b"
)

qwen3_7_plus_config = LLMConfig(
    api_key=get_env_variable("OPENCODE_GO_API_KEY"),
    base_url="https://opencode.ai/zen/go/v1/",
    model_name="qwen3.7-plus"
)

deepseek_v4_pro_config = LLMConfig(
    api_key=get_env_variable("OPENCODE_GO_API_KEY"),
    base_url="https://opencode.ai/zen/go/v1/",
    model_name="deepseek-v4-pro"
)