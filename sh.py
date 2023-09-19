import os
import subprocess
from parse import CommandParser


class Shell:
    def __init__(self):
        self.parser = CommandParser()

    def repl(self):
        while True:
            cmd = input('shell> ')
            if cmd.strip() == 'exit':
                break
            if cmd.startswith("cd"):
                parts = cmd.split()
                if len(parts) > 1:
                    directory = parts[1]
                    os.chdir(directory)
                continue
            parsed = self.parser.command(cmd)
            if parsed['natural_language'] == 'True':
                subprocess.run(['python',
                                '/home/nikhilk/Documents/Personal/smartshell/run_agent.py',
                                f'"{cmd}"'], check=False)
                continue
            if parsed['valid'] == 'False':
                print(parsed['reasoning'])
                if input('Are you sure you want to execute? (y/n): ') != 'y':
                    continue
            subprocess.run(cmd.split(), check=False)


if __name__ == '__main__':
    sh = Shell()
    sh.repl()

