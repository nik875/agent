import http.client
import json
from creds import API_KEY


class APIError(Exception):
    pass


class API:
    FUNCS = [
        'command',
        'chat',
        'generate',
        'debug',
        'session_end'
    ]
    #def __init__(self, host="intellishell.pythonanywhere.com"):
    def __init__(self, sess_id='', host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.sess_id = sess_id
        def endpoint_func(endpoint):
            def func(req: str):
                return self._send_request(f"/{endpoint}", {'request': req})
            return func
        self.endpoints = {i:endpoint_func(i) for i in self.FUNCS}

    def _send_request(self, endpoint, data):
        conn = http.client.HTTPConnection(self.host, self.port)
        # Include API key in headers
        headers = {'Content-Type': 'application/json',
                   'Api-Key': API_KEY}
        data['sess_id'] = self.sess_id
        conn.request("POST", endpoint, json.dumps(data), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        if 'error' in result:
            raise APIError(result['error'])
        return result['response'] if 'response' in result else None

    def session_start(self):
        conn = http.client.HTTPConnection(self.host, self.port)
        # Include API key in headers
        headers = {'Content-Type': 'application/json',
                   'Api-Key': API_KEY}
        conn.request("POST", '/session_start', json.dumps({}), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode())
        if 'error' in result:
            raise APIError(result['error'])
        return result['response']

