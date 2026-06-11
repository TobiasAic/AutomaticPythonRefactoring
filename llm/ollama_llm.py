from llm.openai_llm import OpenAILLM

class OllamaLLM(OpenAILLM):
    def __init__(self, model_name, tools=[]):
        super().__init__(
            api_key="supersecret", # dummy value, Ollama does not require an API key
            base_url="http://localhost:11434/v1",
            model_name=model_name,
            tools=tools
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

    ollama_llm = OllamaLLM("qwen3.5:2b", tools=[weather_tool])
    prompt = "What is the weather like in New York City?"
    response = ollama_llm.generate(prompt)
    print(response)
