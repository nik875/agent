from profiler import ProfilingModule
from action import ActionModule
from externals import ExternalHandler


class Agent:
    def __init__(self, objective):
        self.objective = objective
        self.profiler_module = ProfilingModule(objective)
        self.action_module = ActionModule(self.profiler_module.action_profile())
        self.system = ExternalHandler()

    def run(self):
        planned_action = self.action_module.execute(self.objective)
        print(planned_action)
        input('Press Enter to continue or ctrl+c to abort...')
        result = self.system.do(planned_action)
        print(result)
        return result

