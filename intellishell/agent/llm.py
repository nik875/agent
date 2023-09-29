import guidance
from .creds import OPENAI_API_KEY


class LLMWrapper:
    def __init__(self, role):
        """
        Initialize the OpenAI API with the provided key.
        """
        gpt3 = guidance.llms.OpenAI('gpt-3.5-turbo', api_key=OPENAI_API_KEY)
        self.program = guidance(role, llm=gpt3)
        self.role = role
        self.messages = []

    def prompt(self, **kwargs):
        """
        Given a prompt, format it correctly and ask the agent to generate a response.
        """
        return self.program(boolean_opts=['True', 'False'], **kwargs)

