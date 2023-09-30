from intellishell.parse import CommandParser
from intellishell.chatbot import Chatbot
from intellishell.agent.agent_simple import Agent


class API:
    def __init__(self):
        self.cmd_parser = CommandParser()
        self.chatbot = Chatbot()

    def classify_command(self, cmd: str) -> int:
        """
        Classification codes:
        0: Command
        1: Chat message
        2: Agent action
        """
        if cmd.startswith('?'):
            return 1
        elif cmd.startswith(':'):
            return 2
        return 0

    def validate_command(self, cmd: str) -> str:
        """
        Returns an explanation of exactly what the provided command does.
        """
        return self.cmd_parser.command_simple(cmd)

    def chat(self, cmd: str) -> str:
        return self.chatbot.ask(cmd)

    def gen_code(self, cmd: str) -> str:
        """
        Generates and returns Python code that executes the given command.
        """
        ag = Agent(cmd)
        return ag.run()

