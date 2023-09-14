from llm import LLMAgent
from mem import LongTermMemory
from plan import PlanningModule
from action import ActionModule

# Define global variables for API keys and search engine ID
OPENAI_API_KEY = 'your_openai_api_key'
GOOGLE_API_KEY = 'your_google_api_key'
GOOGLE_CUSTOM_SEARCH_ENGINE_ID = 'your_custom_search_engine_id'

class AutonomousAgent:
    def __init__(self, objective):
        """
        Initialize the Autonomous Agent.

        Args:
            objective (str): The primary objective of the agent.

        Comments:
        - Create an LLMAgent object (renamed as executor) with the provided OpenAI API key and specified objective.
        - Create a LongTermMemory object with a specified maximum size.
        - Create a PlanningModule object with a generator and a critic LLMAgent.
        - Generate a plan using the provided objective.
        - Create an ActionModule object with specified arguments.
        """
        # Create an LLMAgent object and rename it as executor with the provided OpenAI API key
        self.executor = LLMAgent(OPENAI_API_KEY)

        # Create a LongTermMemory object with a specified maximum size
        self.long_term_memory = LongTermMemory(100, OPENAI_API_KEY)

        # Create a PlanningModule object with a generator and a critic LLMAgent
        self.planning_module = PlanningModule(api_key=OPENAI_API_KEY)

        # Generate a plan using the provided objective
        self.planning_module.generate_plan(objective)

        # Create an ActionModule object with specified arguments
        max_token_length = 1000  # Replace with the desired value
        google_api_key = GOOGLE_API_KEY
        custom_search_engine_id = GOOGLE_CUSTOM_SEARCH_ENGINE_ID
        self.action_module = ActionModule(max_token_length, google_api_key, custom_search_engine_id)

    def feedback(self, action_result):
        """
        Provide feedback to the user.

        Args:
            action_result (str): The feedback message to display.
        """
        # Save the result as a local variable plan_feedback
        plan_feedback = self.planning_module.feedback(action_result)

        # Include the action result and plan feedback at the beginning of the prompt
        insight_prompt = f"Action Result: {action_result}\nPlan Feedback: {plan_feedback}\nDevelop one major insight/lesson based on the action result and plan feedback, including keyword terms."

        # Instruct the executor to generate the insight
        major_insight = self.executor.prompt_agent(insight_prompt)

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
            action_prompt = f"Retrieved memory: {relevant_memory}. In the context of this and the step we want to complete, select an action from the provided options."

            # Instruct the Executor to select an action from the options
            selected_action = self.executor.prompt_agent(action_prompt)

            # Create a list to store the arguments
            arguments = []

            # Enter a loop to process arguments for the selected action
            while True:
                # Instruct the Executor to return the next argument (or END if no more arguments)
                next_argument = self.executor.prompt_agent("Return the next argument for the selected action (or END if no more arguments).")

                # If END is received, exit the loop
                if next_argument == "END":
                    break

                # Store each argument in the list
                arguments.append(next_argument)

            # Verify that the selected action is within the dict keys and that the number of arguments matches
            if selected_action not in self.action_module.action_dict:
                self.feedback(f"Invalid action: {selected_action}")
                continue
            callable_fn, num_args = self.action_module.action_dict[selected_action]
            if len(arguments) != num_args:
                self.feedback(f"Invalid number of arguments for action {selected_action}. Expected {num_args}, got {len(arguments)}.")
                continue

            # Continue with the rest of the agent's actions based on the step, relevant_memory, and selected_action
            # ...

            # If continuous is False, provide the planned action to the user along with stored arguments
            if not continuous:
                # Print the planned action and stored arguments
                print(f"Planned Action: {selected_action}")
                print(f"Stored Arguments: {arguments}")
                # Wait for user confirmation
                input("Press Enter to confirm...")
                # Print other relevant information and wait for confirmation
                # ...

            # Call callable_fn on the generated arguments
            try:
                result = callable_fn(*arguments)
            except Exception as e:
                self.feedback(f"Error executing action {selected_action}: {str(e)}")

            # Provide feedback to the planning based on the result of the action
            self.feedback(f"Action result: {result}")

# Rest of the code for LLMAgent, LongTermMemory, PlanningModule, and ActionModule
# ...

# Example usage:
# agent = AutonomousAgent("Your objective here")
# agent.run(continuous=True)  # Run the agent continuously
