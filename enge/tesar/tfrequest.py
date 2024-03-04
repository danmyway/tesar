import json

import requests

from .tfresult import TFResult, TFResultsList

class TFRequest():
    def __init__(self, request_id=None):
        self._request_id = requests_id

    @property
    def id(self):
        return self._send()

    @property
    def payload(self):
        if self._request_id is not None:
            return self.sent_payload
        # TODO
        return json.dumps({
            'msg': 'Hello world!',
        })

    @property
    def sent_payload(self):
        self._send()
        # TODO

    def iter_results(self):
        self._send()
        # TODO
    
    @property
    def results(self):
        return TFResultsList(self.iter_results())

    def wait(self, timeout=-1):
        self._send()
        # TODO
        return False

    def _send(self):
        if self._request_id is not None:
            return self._request_id
        # TODO
        self._request_id = None
        return self._request_id


class TFRequestsList(list):
    def iter_results(self):
        for request in self:
            for result in request.iter_results():
                yield result

    @property
    def results(self):
        return TFResultsList(self.iter_results())
