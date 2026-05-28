from llm.openai_llm import OpenAILLM

class OllamaLLM(OpenAILLM):
    def __init__(self, model_name):
        super().__init__(
            api_key="supersecret", # dummy value, Ollama does not require an API key
            base_url="http://localhost:11434/v1",
            model_name=model_name
        )

# Test if the access to the API works
if __name__ == "__main__":
    ollama_llm = OllamaLLM("qwen3.5:2b")
    prompt = "What is the capital of Germany?"
    response = ollama_llm.generate(prompt)
    print(response)