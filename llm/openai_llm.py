from openai import OpenAI

from llm.llm import LLM


class OpenAILLM(LLM):
    def __init__(self, api_key, base_url, model_name):
        self.model_name = model_name
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content