import os
import sys
import signal
import subprocess
import curses
from parse import CommandParser
from chatbot import Chatbot
from agent.agent_simple import Agent


def handle_backspace(response, stdscr):
    if response:
        response = response[:-1]
        r, c = stdscr.getyx()
        stdscr.move(r, c - 1)
        stdscr.delch()
        stdscr.refresh()
    return response


class Shell:
    SPECIAL_BINS = ['vim', 'nvim', 'hx', 'nano', 'gedit', 'emacs']
    def __init__(self):
        self.parser = CommandParser()
        self.chatbot = Chatbot()
        self.cmd_buffer = []
        self.sel = 0
        self.running_subprocess = None
        self.stdscr = None

    def interrupt_handler(self, signum, frame):
        # pylint: disable=unused-argument
        if self.running_subprocess:
            os.kill(self.running_subprocess.pid, signal.SIGINT)
            self.print('Interrupt signal received')
        else:
            sys.exit()

    def print(self, val):
        self.stdscr.addstr('\n' + val)

    def input(self, prompt, handlers=None):
        handlers = handlers or {}
        handlers[curses.KEY_BACKSPACE] = handle_backspace
        self.stdscr.addstr(prompt)
        response = ''
        while (key := self.stdscr.getch()) != 10:
            if key in handlers:
                response = handlers[key](response, self.stdscr)
                continue
            self.stdscr.addch(key)
            response += chr(key)
        return response

    def execute_cmd(self, cmd):
        if cmd.strip() == 'exit':
            sys.exit(0)
        if cmd.startswith("cd"):
            parts = cmd.split()
            if len(parts) > 1:
                directory = parts[1]
                if os.path.exists(directory) and os.path.isdir(directory):
                    os.chdir(directory)
                else:
                    self.print(f"Directory {directory} not found!")
            return False
        if cmd == 'clear':
            self.stdscr.clear()
            return False
        if 'AGENT:' in cmd:
            prompt = cmd[cmd.find('AGENT:')+len('AGENT:')+1:]
            curses.endwin()
            ag = Agent(prompt)
            ag.run()
            input('Press enter to return to the shell...')
            self.stdscr = curses.initscr()
            return False
        if '?' in cmd:
            self.print(self.chatbot.ask(cmd))
            return False
        parsed = self.parser.command_simple(cmd)
        if parsed != 'Low-risk command' and parsed['valid'] == 'False':
            self.print(parsed['reasoning'])
            if self.input('\nAre you sure you want to execute? (y/n): ') != 'y':
                return False
        try:
            # pylint: disable=subprocess-popen-preexec-fn, global-statement
            binary = cmd.strip().split()[0]
            if binary in self.SPECIAL_BINS:
                with subprocess.Popen(
                    cmd,
                    shell=True,
                    preexec_fn=os.setsid
                ) as self.running_subprocess:
                    self.running_subprocess.communicate()
                    result = False
            else:
                with subprocess.Popen(
                    cmd,
                    shell=True,
                    preexec_fn=os.setsid,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                ) as self.running_subprocess:
                    result = self.running_subprocess.communicate()
        except subprocess.CalledProcessError as e:
            result = e.stdout, e.stderr
        self.running_subprocess = None
        return result

    def repl(self, stdscr):
        self.stdscr = stdscr
        signal.signal(signal.SIGINT, self.interrupt_handler)
        stdscr.scrollok(True)
        def handle_up_arrow(response, stdscr):
            if len(self.cmd_buffer) < 1:
                return response
            if self.sel < len(self.cmd_buffer):
                self.sel += 1
            for _ in response:
                handle_backspace(response, stdscr)
            response = self.cmd_buffer[-self.sel]
            stdscr.addstr(response)
            return response
        def handle_down_arrow(response, stdscr):
            if self.sel == 0:
                return response
            self.sel -= 1
            for _ in response:
                handle_backspace(response, stdscr)
            response = '' if self.sel == 0 else self.cmd_buffer[-self.sel]
            stdscr.addstr(response)
            return response
        handlers = {
            curses.KEY_UP: handle_up_arrow,
            curses.KEY_DOWN: handle_down_arrow
        }

        stdscr.clear()
        while True:
            self.cmd_buffer.append(self.input(f'\n{os.getcwd()}$> ', handlers=handlers))
            self.sel = 0
            if not self.cmd_buffer[-1]:
                continue
            result = self.execute_cmd(self.cmd_buffer[-1])
            if result:
                out, err = result
                out = (out or '') + '\n' if out and err else out or ''
                err = err or ''
                self.print(out + err)

    def main(self):
        curses.wrapper(self.repl)


if __name__ == '__main__':
    sh = Shell()
    sh.main()

