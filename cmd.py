import sys
import traceback
from api import API, APIError


class CmdHandler:
    def __init__(self, sess_id=''):
        self.api = API(sess_id)
        self.to_return = ''
        self.exit_code = 0

    def handle(self, endpoint, cmd):
        try:
            self.to_return = self.api.endpoints[endpoint]({'request': cmd})
        except APIError:
            self.exit_code = 1
            self.to_return = traceback.format_exc()
        # pylint: disable=broad-exception-caught
        except Exception:
            self.exit_code = 2
            self.to_return = traceback.format_exc()

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

