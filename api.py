import http.client
import json
from creds import API_KEY


class APIError(Exception):
    pass


class API:
    FUNCS = [
        'chat',
        'generate',
        'debug',
        'session_end'
    ]
    def __init__(self, sess_id='', host="intellishell.pythonanywhere.com", port=None):
    #def __init__(self, sess_id='', host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.sess_id = sess_id
        self.endpoints = {i:self.to_endpoint_func(i) for i in self.FUNCS}
        self.endpoints['command'] = self.to_endpoint_func('command', timeout=5)
        self.endpoints['output'] = self.to_endpoint_func('output', timeout=5)

    def _send_request(self, endpoint, data, sess_id, timeout=None):
        conn = http.client.HTTPConnection(self.host, timeout=timeout, port=self.port)
        # Include API key in headers
        headers = {'Content-Type': 'application/json',
                   'Api-Key': API_KEY}
        data['sess_id'] = sess_id
        conn.request("POST", endpoint, json.dumps(data), headers)
        response = conn.getresponse()
        try:
            result = json.loads(response.read().decode())
        except json.decoder.JSONDecodeError as e:
            raise APIError('Invalid response from server') from e
        if 'error' in result:
            raise APIError(result['error'])
        return result['response'] if 'response' in result else None

    def to_endpoint_func(self, endpoint, timeout=None):
        return lambda req: self._send_request(f"/{endpoint}", {'request': req}, self.sess_id,
                                              timeout=timeout)

    def session_start(self):
        return self._send_request("/session_start", {}, '')

