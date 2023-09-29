from agent.llm import LLMWrapper


class CommandParser:
    def __init__(self):
        self.system_prompt = """
{{#system~}}
You are a professional Linux customer support assistant with decades of experience. Your job is to
classify the user's input as either shell commands or natural language.
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
        self.cmd_response_time_helper = LLMWrapper(self.system_prompt + """
{{#user~}}
Below is the command I want to run:
```bash
{{command}}
```

For very common commands without unusual flags or arguments, or commands that don't have a high risk
of damage to my system, I want to run them quickly because they're low-stakes. Is this command low-
risk or high-risk? Answer "True" if it's low-risk and "False" if it's high risk.
{{~/user}}

{{#assistant~}}
{{select "risk" options=boolean_opts}}
{{~/assistant}}
        """)
        self.cmd_evaluator = LLMWrapper(self.system_prompt + """
{{#user~}}
Below is the command I want to run:
```bash
{{command}}
```
Help me determine whether this command will execute correctly, is safe to run, and is likely to do
what I intended to do. Reason aloud in 1-2 sentences.
{{~/user}}

{{#assistant~}}
{{gen "reasoning" max_tokens=250}}
{{~/assistant}}

{{#user~}}
Now make a final determination on whether this is a fully valid bash command that probably does
exactly what I intended. If you have any doubts at all about possible reasons that the user's
command might not do what they want, answer with "False". Assume that the user is a new Linux user
who is prone to making simple mistakes. Help them catch these mistakes.
{{~/user}}

{{#assistant~}}
{{select "valid" options=boolean_opts}}
{{~/assistant}}
        """)

    def command(self, cmd):
        mode = self.mode_selector.prompt(command=cmd, opts=['Natural language', 'Shell command'])
        if mode['natural_language'] == 'Natural language':
            return 'Chat'
        return self.command_simple(cmd)

    def command_simple(self, cmd):
        #risk = self.cmd_response_time_helper.prompt(command=cmd)['risk']
        #if risk == 'True':
        #    return 'Low-risk command'
        return self.cmd_evaluator.prompt(command=cmd)

