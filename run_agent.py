import sys
from agent.agent import Agent


if __name__ == '__main__':
    # Check if there's a command line argument provided
    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        task = input("Please enter a prompt for the agent: ")

    a = Agent(task)
    a.run()

