from utility.enviroment_variables import get_env_variable
from llm.openai_llm import OpenAILLM

class BigPickle(OpenAILLM):
    def __init__(self, tools=[]):
        super().__init__(
            api_key=get_env_variable("OPENCODE_API_KEY"),
            base_url="https://opencode.ai/zen/v1",
            model_name="big-pickle",
            tools=tools,
        )

# Test if the access to the API works
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

    big_pickle = BigPickle(tools=[weather_tool])
    prompt = "What is the weather like in New York City?"
    response = big_pickle.generate(prompt)
    print(response)

