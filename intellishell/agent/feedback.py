from .llm import LLMWrapper


class Feedback:
    def __init__(self, step_complete, revise_plan, fb_str, new_mem=''):
        self.step_complete = step_complete
        self.revise_plan = revise_plan
        self.fb_str = fb_str
        self.new_mem = new_mem

    def __str__(self):
        result = 'Feedback: ' + self.fb_str if self.revise_plan else ''
        result = f'{result}\nNewMem: {self.new_mem}' if self.new_mem else result
        result += f"SC:{self.step_complete};RP:{self.revise_plan}"
        return result


class FeedbackModule:
    def __init__(self, profile, planning_module, memory_module):
        self.planning_module = planning_module
        self.memory_module = memory_module
        self.model = LLMWrapper(profile)

    def feedback(self, attempted_action, result):
        attempted_step = self.planning_module.plan.popleft()
        self.planning_module.done.append(attempted_step)
        raw_feedback = self.model.prompt(
            attempted_step=attempted_step,
            attempted_action=attempted_action,
            result=result,
            completed_steps=self.planning_module.done,
            current_plan=self.planning_module.plan
        )
        feedback = Feedback(
            raw_feedback['STEP_COMPLETE'] == 'True',
            raw_feedback['REVISE_PLAN'] == 'True',
            raw_feedback['MAIN_CONTENT']
        )
        if not feedback.step_complete:
            self.planning_module.plan.appendleft(attempted_step)
            self.planning_module.done.pop()
        new_mem = self.memory_module.gen_memory(attempted_step, attempted_action, result, feedback)
        feedback.new_mem = new_mem
        if feedback.revise_plan:
            self.planning_module.gen_plan(feedback)
        return feedback

