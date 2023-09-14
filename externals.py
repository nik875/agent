import subprocess


class ExternalHandler:
    def __init__(self):
        pass

    def do(self, action):
        with open('agent_action.py', 'w') as f:
            f.write(action)
        with subprocess.Popen(
            ['python', 'agent_action.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Ensure the output is in text format
        ) as process:
            stdout, stderr = process.communicate()

        # Combine stdout and stderr
        output = f"stdout:\n{stdout}\n\nstderr:\n{stderr}"
        return output

