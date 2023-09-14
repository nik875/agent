from llm import LLMAgent
from profiler import parse_generation


class Feedback:
    def __init__(self, step_complete, obj_complete, revise_plan, fb_str, new_mem=''):
        self.step_complete = step_complete
        self.obj_complete = obj_complete
        self.revise_plan = revise_plan
        self.fb_str = fb_str
        self.new_mem = new_mem

    def __str__(self):
        result = 'Feedback: ' + self.fb_str if self.revise_plan else ''
        result = f'{result}\nNewMem: {self.new_mem}' if self.new_mem else result
        return result


class FeedbackModule:
    def __init__(self, profile, planning_module, memory_module):
        self.planning_module = planning_module
        self.memory_module = memory_module
        self.model = LLMAgent(profile)

    def feedback(self, attempted_step, attempted_action, result):
        raw_feedback = self.model.prompt(f"""
Generate feedback based on the following:
$ATTEMPTED_STEP: {attempted_step}

$ATTEMPTED_ACTION: {attempted_action}

$RESULT: {result}

$CURRENT_PLAN: {self.planning_module.raw_plan}
        """)
        as_dict = parse_generation(raw_feedback)
        feedback = Feedback(
            bool(as_dict['STEP_COMPLETE']),
            bool(as_dict['OBJ_COMPLETE']),
            bool(as_dict['REVISE_PLAN']),
            as_dict['MAIN_CONTENT']
        )
        new_mem = self.memory_module.gen_memory(attempted_step, attempted_action, result, feedback)
        feedback.new_mem = new_mem
        self.memory_module.add_memory(new_mem)
        if feedback.revise_plan:
            self.planning_module.gen_plan(feedback)
        return feedback

