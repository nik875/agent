import sys
from api import API


class CmdHandler:
    def __init__(self, sess_id=''):
        self.api = API(sess_id)
        self.to_return = ''
        self.exit_code = 0

    def handle(self, endpoint, cmd):
        self.to_return = self.api.endpoints[endpoint]({'request': cmd})

    def exit(self):
        if self.to_return:
            print(self.to_return)
        sys.exit(self.exit_code)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        api = API()
        result = api.session_start()
        print(result)
        sys.exit(0)
    handler = CmdHandler(sys.argv[2])
    handler.handle(sys.argv[1], sys.argv[3])
    handler.exit()

