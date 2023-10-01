import http.client
import json
from creds import API_KEY


class APIError(Exception):
    pass


class API:
    def __init__(self, host="intellishell.pythonanywhere.com"):
        self.host = host

    def _send_request(self, endpoint, data):
        conn = http.client.HTTPSConnection(self.host)
        headers = {'Content-Type': 'application/json', 'Api-Key': API_KEY}  # Include API key in headers
        conn.request("POST", endpoint, json.dumps(data), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        if 'error' in result:
            raise APIError(result['error'])
        return result

    def classify_command(self, cmd: str) -> int:
        data = self._send_request("/classify_command", {"cmd": cmd})
        return data.get("classification")

    def chat(self, hist: str) -> str:
        data = self._send_request("/chat", {"hist": hist})
        return data.get("chat_history")

    def validate_command(self, cmd: str) -> str:
        data = self._send_request("/validate_command", {"cmd": cmd})
        return data.get("validation")

    def gen_code(self, cmd: str) -> str:
        data = self._send_request("/gen_code", {"cmd": cmd})
        return data.get("generated_code")

# Usage
if __name__ == '__main__':
    api_client = API()
    command = "?hello"
    classification = api_client.classify_command(command)
    print(f"The command '{command}' is of type: {classification}")

