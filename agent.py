from llm import LLMAgent
from mem import LongTermMemory
from plan import PlanningModule
from action import ActionModule
from creds import *


class AutonomousAgent:
    def __init__(self, objective):
        """
        Initialize the Autonomous Agent.

        Args:
            objective (str): The primary objective of the agent.

        Comments:
        - Create an ActionModule object with specified arguments.
        - Create an LLMAgent object (renamed as executor) with the provided OpenAI API key and specified objective.
        - Create a LongTermMemory object with a specified maximum size.
        - Create a PlanningModule object with a generator and a critic LLMAgent.
        - Generate a plan using the provided objective.
        """
        # Create an ActionModule object with specified arguments
        max_token_length = 1000  # Replace with the desired value
        google_api_key = GOOGLE_API_KEY
        custom_search_engine_id = GOOGLE_CUSTOM_SEARCH_ENGINE_ID
        self.action_module = ActionModule(max_token_length, google_api_key, custom_search_engine_id)

        # Generate the 'insert_actions' string programmatically, including action descriptions
        actions_with_descriptions = []
        for action_name, (_, _, description) in self.action_module.action_dict.items():
            actions_with_descriptions.append(f"{action_name}: {description}")
        insert_actions = ", ".join(actions_with_descriptions)

        # Create an LLMAgent object and rename it as executor with the provided OpenAI API key
        self.executor = LLMAgent(OPENAI_API_KEY)
        self.executor.create_agent(
            f"Understand natural language instructions, find relevant memories, generate actions, and generate insights from the whole process. The following are allowed actions:\n{insert_actions}\nTo find memories, generate a short set of search terms (e.g., to find memories about installing the OpenAI package, search for 'python package install openai pip'). To generate insights, analyze the previous action and its feedback and write a single-sentence lesson that can be learned from what happened, including keyword terms that can be used to find this memory later."
        )

        # Create a LongTermMemory object with a specified maximum size
        self.long_term_memory = LongTermMemory(100, OPENAI_API_KEY)

        # Create a PlanningModule object with a generator and a critic LLMAgent
        self.planning_module = PlanningModule(api_key=OPENAI_API_KEY)

        # Generate a plan using the provided objective
        self.planning_module.generate_plan(objective)

    def feedback(self, action_result):
        """
        Provide feedback to the user.

        Args:
            action_result (str): The feedback message to display.
        """
        # Save the result as a local variable plan_feedback
        plan_feedback = self.planning_module.feedback(action_result)
        print(f'DEBUG: Plan Feedback: {plan_feedback}')

        # Include the action result and plan feedback at the beginning of the prompt
        insight_prompt = f"Action Result: {action_result}\nPlan Feedback: {plan_feedback}\nDevelop one major insight/lesson based on the action result and plan feedback, including keyword terms."

        # Instruct the executor to generate the insight
        major_insight = self.executor.prompt_agent(insight_prompt)
        print(f'DEBUG: Major insight: {major_insight}')

        # Store the generated insight in long-term memory
        self.long_term_memory.add_memory(major_insight)

    def run(self, continuous=False):
        """
        Run the main loop of the agent.

        Args:
            continuous (bool, optional): Whether the agent should run continuously. Defaults to False.

        Comments:
        - Execute the planning's next_step.
        - Instruct the Executor to generate search terms for a relevant memory for this new step.
        - Use the Memory module to find the relevant memory.
        - Instruct the Executor to select an action.
        - Enter a loop to process arguments for the selected action:
            - Instruct the Executor to return the next argument (or END if no more arguments).
            - If END is received, exit the loop.
            - Store each argument in a list.
        - Verify that the selected action is within the dict keys and that the number of arguments matches.
        - If continuous is False, provide the planned action to the user and wait for confirmation, including the stored arguments.
        - Execute the relevant action using the ActionModule.
        - Provide feedback to the planning based on the result of the action.
        - Instruct the Executor to generate a major insight based on the feedback and the overall process.
        """
        self.continuous = continuous

        while (step := self.planning_module.next_step()) is not None:
            # Instruct the Executor to generate search terms for the new step
            search_terms = self.executor.prompt_agent(f"Generate search terms for a relevant memory for this new step: {step}")

            # Use the Memory module to find the relevant memory
            relevant_memory = self.long_term_memory.find_memory(search_terms)

            # Instruct the Executor to prompt with the retrieved memory and action options
            action_prompt = f"Retrieved memory: {relevant_memory}. In the context of this and the step we want to complete, select an action name. Ensure that the following is in your output: 'SELECTED_ACTION: action_name'."

            # Instruct the Executor to select an action from the options
            result = self.executor.prompt_agent(action_prompt)
            selected_action = result[result.find('SELECTED_ACTION: ')+len('SELECTED_ACTION: '):]
            selected_action = selected_action.split(' ')[0]
            # Verify that the selected action is within the dict keys and that the number of arguments matches
            if selected_action not in self.action_module.action_dict:
                self.feedback(f"Invalid action: {selected_action}")
                continue
            callable_fn, num_args, _ = self.action_module.action_dict[selected_action]

            # Create a list to store the arguments
            arguments = []
            # Enter a loop to process arguments for the selected action
            for _ in range(num_args):
                # Instruct the Executor to return the next argument (or END if no more arguments)
                next_argument = self.executor.prompt_agent("Return your next argument for the selected action (or END if no more arguments). Generate only one argument at a time. This is how you will perform the action, so be sure to fill in the arguments with your own ideas. Ensure that the following is at the end of your output: 'NEXT_ARG: YOUR_GENERATED_ARG_OR_END'")
                # If END is received, exit the loop
                if 'END' in next_argument:
                    break
                next_argument = next_argument[next_argument.rfind('NEXT_ARG: ')+len('NEXT_ARG: '):]
                # Store each argument in the list
                arguments.append(next_argument)

            print(f'DEBUG: action: {selected_action}, args: {arguments}')
            if len(arguments) != num_args:
                self.feedback(f"Invalid number of arguments for action {selected_action}. Expected {num_args}, got {len(arguments)}.")
                continue

            # If continuous is False, provide the planned action to the user along with stored arguments
            if not continuous:
                print(f"Planned Action: {selected_action}")
                print(f"Stored Arguments: {arguments}")
                input("Press Enter to confirm...")

            # Call callable_fn on the generated arguments
            try:
                result = callable_fn(*arguments)
            except Exception as e:
                self.feedback(f"Error executing action {selected_action}: {str(e)}")
            finally:
                # Provide feedback to the planning based on the result of the action
                self.feedback(f"Action result: {result}")

# Example usage:
# agent = AutonomousAgent("Your objective here")
# agent.run(continuous=True)  # Run the agent continuously
