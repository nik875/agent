from .llm import LLMWrapper


class ActionModule:
    def __init__(self, profile):
        self.model = LLMWrapper(profile)

    def execute(self, planned_step, memory='No memory', feedback='No feedback'):
        generation = self.model.prompt(
            planned_step=planned_step,
            relevant_memory=memory,
            feedback=feedback
        )
        return generation['MAIN_CONTENT']

