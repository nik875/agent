from llm import LLMAgent
from profiler import parse_generation


class ActionModule:
    def __init__(self, profile):
        self.model = LLMAgent(profile)

    def execute(self, planned_step, memory=None):
        generation = self.model.prompt(f"""
Generate an action given the following:
$PLANNED_STEP: {planned_step}
$RELEVANT_MEMORY: {memory}
        """)
        as_dict = parse_generation(generation)
        return as_dict['MAIN_CONTENT']

