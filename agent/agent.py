from .profiler import ProfilingModule
from .mem import MemoryModule
from .plan import PlanningModule
from .action import ActionModule
from .externals import ExternalHandler
from .feedback import FeedbackModule


class Agent:
    def __init__(self, objective):
        self.profiler_module = ProfilingModule(objective)
        self.memory_module = MemoryModule(self.profiler_module.memory_profile())
        self.planning_module = PlanningModule(self.profiler_module.planner_profile())
        self.action_module = ActionModule(self.profiler_module.action_profile())
        self.system = ExternalHandler()
        self.feedback_module = FeedbackModule(
            self.profiler_module.feedback_profile(),
            self.planning_module,
            self.memory_module
        )

    def run(self, continuous=False):
        self.planning_module.gen_plan()
        feedback = ''
        while not self.planning_module.plan_complete():
            print('-' * 40)
            current_step = self.planning_module.current_step()
            print(f'Currently doing: {current_step}')
            recent_memory = self.memory_module.relevant_memory(current_step)
            planned_action = self.action_module.execute(current_step, recent_memory, str(feedback))
            result = None
            if not continuous:
                print(f'Planned action: {planned_action}')
                if fb := input('Press enter to proceed or provide human feedback: '):
                    if fb == 'SKIP':
                        continue
                    result = f'Action not completed due to user intervention. User feedback: {fb}'
            if not result:
                result = self.system.do(planned_action)
            print(f'Result of execution: {result}')
            feedback = self.feedback_module.feedback(planned_action, result)
            print(f'Feedback: {feedback}')
        print('Objective complete! Exiting.')

