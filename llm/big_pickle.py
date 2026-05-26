from openai import OpenAI

from utility.enviroment_variables import get_env_variable
from llm.llm import LLM


class BigPickle(LLM):
    def __init__(self):
        self.client = OpenAI(
            api_key=get_env_variable("OPENCODE_API_KEY"),
            base_url="https://opencode.ai/zen/v1",
        )

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="big-pickle",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

# Test if the access to the API works
if __name__ == "__main__":
    big_pickle = BigPickle()
    prompt = "What is the capital of France?"
    response = big_pickle.generate(prompt)
    print(response)