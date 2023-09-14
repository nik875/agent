from collections import deque
from llm import LLMAgent

class PlanningModule:
    def __init__(self, api_key, action_dict):
        """
        Initialize the PlanningModule with an agent (LLMAgent).
        """
        actions_with_descriptions = []
        for action_name, (_, _, description) in action_dict.items():
            actions_with_descriptions.append(f"{action_name}: {description}")
        insert_actions = ", ".join(actions_with_descriptions)
        self.agent = LLMAgent(api_key)
        self.agent.create_agent(f"Generate thorough, step-by-step, bite-sized plans to accomplish high-level goals and provide constructive criticisms of those plans. The following are allowed actions:\n{insert_actions}\nYour plans should involve steps which are possible to accomplish with just one action each. Assume nothing about what files exist and at what paths, and assume nothing about the user's system.")

        # Create instance variable for objective
        self.objective = None

        # Create an empty plan queue
        self.plan = deque()


    def gen_plan(self, prompt):
        plan_description = self.agent.prompt_agent(prompt)
        print(plan_description)
        self.plan = deque()
        for line in plan_description.strip().split('\n'):
            expected_header = f'{len(self.plan)+1}. Step {len(self.plan)+1}: '
            if line.startswith(expected_header):
                self.plan.append(line.lstrip(expected_header))

    def generate_plan(self, objective):
        """
        Given a high-level objective, generate and save a series of concrete, tangible steps.
        """
        self.objective = objective
        prompt = f"Generate a detailed and easy-to-follow plan to accomplish the following objective: '{objective}'. Each step should be small and easy to complete. A longer, more specific plan is preferred over a short, unclear one. The plan should be structured as follows:\n1. Step 1: [Your instruction here]\n2. Step 2: [Your instruction here]\n3. Step 3: [Your instruction here]\n\nProvide the plan ONLY in the requested format, and do not include any additional information or content. Do not generate text at the beginning or end; only generate the plan steps as a numbered list."
        self.gen_plan(prompt)

    def next_step(self):
        if self.plan:
            return self.plan[0]
        else:
            return None

    def feedback(self, text):
        current_step = self.plan[0]
        # Edit the second prompt to remove redundancy and remove current plan and step
        prompt = f"Real-world Result:\n{text}\n\nProvide feedback to help improve the current step. Specifically, consider the following:\n1. Are we moving in the right direction to achieve the objective?\n2. If not, what adjustments can be made to the current step to make it more effective?\n\nMake a y/n judgement on whether the current step has been completed. Indicate whether a revision is needed ('REVISION_NEEDED: <y/n>'). Generate feedback in the following format: 'STEP_COMPLETED: <y/n>. REVISION_NEEDED: <y/n>. FEEDBACK: <feedback here>'"
        feedback_text = self.agent.prompt_agent(prompt)
        
        # Split the feedback text into its components
        step_completion, revision_needed, critic_feedback = self.parse_feedback(feedback_text)
        
        if step_completion == "y":
            self.plan.popleft()
        
        if revision_needed == "y":
            self.revise_plan(critic_feedback)
        
        return feedback_text

    def revise_plan(self, feedback):
        current_step = self.plan[0]
        current_objective = f"Your overarching goal is: {self.objective}"
        prompt = f"{current_objective}\nCurrent Step:\n{current_step}\nGiven feedback: {feedback}\n\nRefer back to the plan you are currently following and generate a revised version. This revised plan will be the one you will follow from now on. Each step should be small, easy to complete, and contribute to achieving the overarching goal. The plan should be structured as follows:\n1. Step 1: [Your instruction here]\n2. Step 2: [Your instruction here]\n3. Step 3: [Your instruction here]\n\nProvide the revised plan ONLY in the requested format, and do not include any additional information or content."
        self.gen_plan(prompt)

    def parse_feedback(self, feedback_text):
        try:
            feedback_parts = feedback_text.split(". ")
            step_completion = feedback_parts[0].split(": ")[1].strip()
            revision_needed = feedback_parts[1].split(": ")[1].strip()
            critic_feedback = feedback_parts[2].split(": ")[1].strip()
            return step_completion, revision_needed, critic_feedback
        except IndexError:
            return 'n', 'y', feedback_text
