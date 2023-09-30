from .agent.llm import LLMWrapper


class CommandParser:
    def __init__(self):
        self.system_prompt = """
{{#system~}}
You are a professional Linux customer support assistant with decades of experience. Your job is to
help the user run commands on their system.
{{~/system}}
        """
        self.mode_selector = LLMWrapper(self.system_prompt + """
{{#user~}}
Here's my message:
```
{{command}}
```
Is this a natural language chat message sent to an AI assistant, or is it an attempted shell
command?
{{~/user}}

{{#assistant~}}
{{select "natural_language" options=opts}}
{{~/assistant}}
        """)
        self.cmd_evaluator = LLMWrapper(self.system_prompt + """
{{#user~}}
Below is the command I want to run:
```bash
{{command}}
```
Explain in plain English what this command does, whether it's likely to do what I intended, and
whether it's safe to run. Reason aloud in 1-2 sentences.
{{~/user}}

{{#assistant~}}
{{gen "reasoning" max_tokens=250}}
{{~/assistant}}
        """)

    def command(self, cmd):
        mode = self.mode_selector.prompt(command=cmd, opts=['Natural language', 'Shell command'])
        if mode['natural_language'] == 'Natural language':
            return 'Chat'
        return self.command_simple(cmd)

    def command_simple(self, cmd):
        return self.cmd_evaluator.prompt(command=cmd)['reasoning']

