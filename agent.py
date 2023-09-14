from profiler import ProfilingModule
from mem import MemoryModule
from plan import PlanningModule
from action import ActionModule
from externals import ExternalHandler
from feedback import FeedbackModule


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
        while True:
            print('-' * 40)
            next_step = self.planning_module.next_step()
            if not next_step:
                self.planning_module.gen_plan()
                print(f'New Plan: {self.planning_module.raw_plan}')
                next_step = self.planning_module.next_step()
            print(f'Currently doing: {next_step}')
            recent_memory = self.memory_module.relevant_memory(next_step)
            planned_action = self.action_module.execute(next_step, recent_memory)
            result = None
            if not continuous:
                print(f'Planned action: {planned_action}')
                if fb := input('Press enter to proceed or provide human feedback: '):
                    result = f'Action not completed due to user intervention. User feedback: {fb}'
            if not result:
                result = self.system.do(planned_action)
            print('Finished action execution')
            feedback = self.feedback_module.feedback(next_step, planned_action, result)
            print(f'Feedback: {feedback}')
            if feedback.obj_complete:
                print('Objective complete! Exiting.')
                return

