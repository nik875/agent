import collections
from .llm import LLMWrapper


class PlanningModule:
    def __init__(self, profile):
        self.plan_generator = LLMWrapper(profile[0])
        self.plan_criticizer = LLMWrapper(profile[1])
        self.plan = collections.deque()
        self.done = collections.deque()
        self.raw_plan = ''

    def current_step(self):
        return self.plan[0] if self.plan else None

    def next_step(self):
        if self.plan:
            self.done.append(self.plan.popleft())

    def plan_complete(self):
        return len(self.plan) == 0

    def parse_plan(self, raw_plan):
        plan = collections.deque()
        for line in raw_plan.strip().split('\n'):
            expected_header = f'Step {len(plan)}: '
            if line.startswith(expected_header):
                plan.append(line.lstrip(expected_header))
        return plan

    def gen_plan(self, feedback='No feedback'):
        print('Generating plan...')
        generation = self.plan_generator.prompt(
            feedback=feedback,
            completed_steps=self.done,
            old_plan=self.plan,
        )
        self.raw_plan = generation['MAIN_CONTENT']
        self.plan = self.parse_plan(self.raw_plan)
        for _ in range(7):
            print('Refining plan...')
            feedback = self.plan_criticizer.prompt(
                completed_steps=self.done,
                plan=self.plan,
            )
            print('Feedback: ' + feedback['MAIN_CONTENT'])
            generation = self.plan_generator.prompt(
                feedback=feedback['MAIN_CONTENT'],
                completed_steps=self.done,
                old_plan=self.plan,
            )
            self.raw_plan = generation['MAIN_CONTENT']
            self.plan = self.parse_plan(self.raw_plan)
        print('New plan:')
        print(self.plan)

