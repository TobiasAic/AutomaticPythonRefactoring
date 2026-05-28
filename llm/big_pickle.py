from utility.enviroment_variables import get_env_variable
from llm.openai_llm import OpenAILLM

class BigPickle(OpenAILLM):
    def __init__(self):
        super().__init__(
            api_key=get_env_variable("OPENCODE_API_KEY"),
            base_url="https://opencode.ai/zen/v1",
            model_name="big-pickle"
        )

# Test if the access to the API works
if __name__ == "__main__":
    big_pickle = BigPickle()
    prompt = "What is the capital of France?"
    response = big_pickle.generate(prompt)
    print(response)