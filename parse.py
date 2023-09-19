from agent.llm import LLMWrapper


class CommandParser:
    def __init__(self):
        self.model = LLMWrapper("""
{{#system~}}
You are a professional Linux customer support assistant with decades of experience. Your job is to
help the user determine whether the command that they provide you is a valid Bash command or a
natural language instruction.
{{~/system}}

{{#user~}}
Below is the command I want to run:
```bash
{{command}}
```
Is this a natural language instruction? Answer "True" for yes and "False" for no.
{{~/user}}

{{#assistant~}}
{{select "natural_language" options=boolean_opts}}
{{~/assistant}}

{{#user~}}
Think out loud and explain to me what this command does, whether it's valid, and whether it would
perform the task that the user intended.
{{~/user}}

{{#assistant~}}
{{gen "reasoning" max_tokens=250}}
{{~/assistant}}

{{#user~}}
Now make a final determination on whether this is a fully valid bash command that probably does
exactly what the user intended. If you have any doubts at all about possible reasons that the user's
command might not do what they want, answer with "False".
{{~/user}}

{{#assistant~}}
{{select "valid" options=boolean_opts}}
{{~/assistant}}
        """)

    def command(self, cmd):
        return self.model.prompt(command=cmd)

