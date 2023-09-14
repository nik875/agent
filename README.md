# Autonomous Agent

To use, it's necessary to create a creds.py file with the following content:


```python
OPENAI_API_KEY = 'your-key-here'
GOOGLE_API_KEY = 'your-key-here'
GOOGLE_CUSTOM_SEARCH_ENGINE_ID = 'your-engine-id-here'
```

terrible documentation:

- init(objective):
    - create a new llm agent with objective: "understand natural language instructions, find relevant memories, generate actions, and generate insights from the whole process. the following are allowed actions: {insert_actions}. to find memories, generate a short set of search terms (e.g. to find memories about installing the openai package, search for 'python package install openai pip'). to generate insights, analyze the previous action and its feedback and write a single-sentence lesson that can be learned from what happened, including keyword terms that can be used to find this memory later." this is the executor.
    - also create a PlanningModule object using the api key.
        - call generate_plan on the planning object with the objective provided by the user as an argument to init.
    - also create a LongTermMemory object using a max_size of 100 and the same openai api key.
    - also create ActionModule with max_token_length 1000, google_custom_search_api_key and google_custom_search_engine_id defined by the values at the top
- run(continuous=False): main loop.
    - plan.next_step()
    - tell executor to generate search terms to find a memory relating to the given step
    - memory.find_memory()
    - executor: select an action
    - loop:
        - executor: return next argument (or END if no more arguments for this action)
        - if END, break loop
    - if continuous==False, tell user the planned action and wait for their confirmation
    - run the relevant action using action_module
    - plan.feedback(result of action)
    - executor: given this {feedback} and everything else that happened over the course of the previous action, generate a major insight to save for the future.
    - memory.add_memory(insight)
