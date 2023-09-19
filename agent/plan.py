import collections
from .llm import LLMWrapper


class PlanningModule:
    def __init__(self, profile):
        self.model = LLMWrapper(profile)
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
            expected_header = f'Step {len(plan)+1}: '
            if line.startswith(expected_header):
                plan.append(line.lstrip(expected_header))
        return plan

    def gen_plan(self, feedback='No feedback'):
        generation = self.model.prompt(
            feedback=feedback,
            old_plan=self.done + self.plan if self.done or self.plan else 'No old plan',
            broadness_levels=['too specific', 'too general', 'just right']
        )
        self.raw_plan = generation['MAIN_CONTENT']
        self.plan = self.parse_plan(self.raw_plan)
        print('Initial plan:')
        print(self.raw_plan)
        for _ in range(7):
            if generation['END'] == 'just right':
                break
            print(f"Plan was {generation['END']}")
            print('Refining plan...')
            generation = self.model.prompt(
                feedback=f"The last plan was {generation['END']}. Adjust accordingly.",
                old_plan=self.done + self.plan if self.done or self.plan else 'No old plan',
                broadness_levels=['too specific', 'too general', 'just right']
            )
            self.raw_plan = generation['MAIN_CONTENT']
            self.plan = self.parse_plan(self.raw_plan)
            print(self.raw_plan)
            print('-'*20)

