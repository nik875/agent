from collections import deque
import openai
import tiktoken
from .agent.creds import OPENAI_API_KEY


class Chatbot:
    def __init__(self, max_tokens=4097):
        openai.api_key = OPENAI_API_KEY
        self.role = {'role': 'system', 'content': """
You are a professional Linux sysadmin with decades of experience in customer support. Your job is to
help the user perform tasks on their computer and answer their questions.
        """
}
        self.messages = deque([self.role])
        self.objective = None
        self.max_context_len = max_tokens

    def num_tokens_from_messages(self, model="gpt-3.5-turbo-0613"):
        """
        Return the number of tokens used by a list of messages.
        src: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in self.messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def ask(self, prompt):
        """
        Ask a question of the chatbot
        """
        # Remind the model of its role and the overarching objective
        self.messages.append({"role": "user", "content": prompt})
        while self.num_tokens_from_messages() > self.max_context_len:
            self.messages.popleft()
            self.messages.popleft()
            self.messages.appendleft(self.role)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=list(self.messages)
        )
        agent_response = response.choices[0].message['content']
        self.messages.append({"role": "assistant", "content": agent_response})
        return agent_response

