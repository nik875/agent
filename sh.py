import os
import subprocess
from parse import CommandParser
from chatbot import Chatbot


class Shell:
    def __init__(self):
        self.parser = CommandParser()
        self.chatbot = Chatbot()

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
            if 'AGENT:' in cmd:
                prompt = cmd[cmd.find('AGENT:')+len('AGENT:')+1:]
                subprocess.run(['python',
                                '/home/nikhilk/Documents/Personal/smartshell/run_agent.py',
                                f'"{prompt}"'], check=True)
                continue
            parsed = self.parser.command(cmd)
            if parsed == 'Chat':
                print(self.chatbot.ask(cmd))
                continue
            if parsed != 'Low-risk command' and parsed['valid'] == 'False':
                print(parsed['reasoning'])
                if input('Are you sure you want to execute? (y/n): ') != 'y':
                    continue
            try:
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                continue


if __name__ == '__main__':
    sh = Shell()
    sh.repl()

