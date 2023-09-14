import openai
from mem import LongTermMemory

class LLMAgent:
    def __init__(self, api_key):
        """
        Initialize the OpenAI API with the provided key.
        """
        openai.api_key = api_key
        self.messages = []
        self.objective = None

    def create_agent(self, objective):
        """
        Given a high-level objective, create a fresh LLM instance to generate an appropriate role for the agent.
        """
        self.objective = objective
        self.messages.append({"role": "user", "content": f"Define a role for an agent to accomplish the objective: {objective}"})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        role = response.choices[0].message['content']
        self.messages.append({"role": "assistant", "content": role})
        return role

    def prompt_agent(self, prompt):
        """
        Given a prompt, format it correctly and ask the agent to generate a response.
        """
        # Remind the model of its role and the overarching objective
        self.messages.append({"role": "system", "content": f"You are an agent with the role: {self.messages[-1]['content']}. Your overarching objective is: {self.objective}"})
        self.messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        agent_response = response.choices[0].message['content']
        self.messages.append({"role": "assistant", "content": agent_response})
        return agent_response

# Example usage:
# agent = AutonomousAgent("YOUR_OPENAI_API_KEY")
# agent.create_agent("Write a Python class")
# response = agent.prompt_agent("How do I start?")
# print(response)
