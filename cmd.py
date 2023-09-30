import sys
from api import API


class CmdHandler:
    def __init__(self):
        self.api = API()
        self.to_return = ''
        self.exit_code = 0

    def handle(self, cmd):
        self.exit_code = self.api.classify_command(cmd)
        if self.exit_code == 0:
            self.to_return = self.api.validate_command(cmd)
        elif self.exit_code == 1:
            self.to_return = cmd.lstrip('?')
        elif self.exit_code == 2:
            self.to_return = self.api.gen_code(cmd.lstrip(':'))
        else:
            self.to_return = "Input type not implemented!"

    def chat(self, hist):
        self.to_return = self.api.chat(hist)

    def exit(self):
        print(self.to_return)
        sys.exit(self.exit_code)


if __name__ == '__main__':
    handler = CmdHandler()
    if len(sys.argv) == 3 and sys.argv[1] == '--chat':
        handler.chat(sys.argv[2])
    else:
        handler.handle(sys.argv[1])
    handler.exit()

