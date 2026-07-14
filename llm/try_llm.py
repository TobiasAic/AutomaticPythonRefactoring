""" Little script to test the LLM implementations and LLM availability. """

from llm.openai_llm import OpenAILLM
from llm.llm_presets import big_pickle_config, qwen3_5_2b_config

if __name__ == "__main__":
    weather_tool = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        },
    }

    llm = OpenAILLM(config=big_pickle_config)
    prompt = "What is the weather like in New York City?"
    response = llm.generate(prompt, tools=[weather_tool])
    print(response)

