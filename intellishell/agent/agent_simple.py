import sys
from .profiler import ProfilingModule
from .action import ActionModule


class Agent:
    def __init__(self, objective):
        self.objective = objective
        self.profiler_module = ProfilingModule(objective)
        self.action_module = ActionModule(self.profiler_module.action_profile())

    def run(self):
        planned_action = self.action_module.execute(self.objective)
        if "```python" in planned_action:
            planned_action = planned_action[planned_action.find("```python")+len("```python"):]
            planned_action = planned_action[:planned_action.find("```")]
        return planned_action


if __name__ == '__main__':
    argv = sys.argv[1]
    ag = Agent(argv)
    print(ag.run())

