import functools

import json
import requests

from .tfresult import TFResult, TFResultsList

def frozen_after_send(wrapped):
    @functools.wraps(wrapped)
    def wrapper(self, *args, **kwargs):
        if self._frozen:
            raise Exception("Can't do that! FROZEN!")
        return wrapped(self, *args, **kwargs)
    return wrapper

class TFEnvironment():
    #  arch
    #  os/compose
    #  pool
    #  variables
    #  artifacts
    #  settings/provisioning
    #   post_install_script
    #   tags/BusinessUnit
    #  tmt/context
    #   distro
    #   arch
    pass

class TFRequest():
    PROPERTIES = {
        # test/fmf
        'git_url' : None,
        'git_branch' : None,
        'git_path' : None,
        'plan_name' : None,
        'plan_filter' : None,
        'test_filter' : None,
        # environments (list)
        'environments' : None,
    }
    def __init__(self, request_id=None, **kwargs):
        self._request_id = request_id
        self._setup_properties(**kwargs)

    def _setup_properties(self, **kwargs):
        for propname, default_value in self.PROPERTIES.items():
            setattr(self, propname, default_value)
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(key)
            setattr(self, key, value)

    def copy(self, **kwargs):
        copy_properties = kwargs.copy()
        for propname in self.PROPERTIES:
            copy_properties.setdefault(propname, getattr(self, propname))
        return TFRequest(**copy_properties)

    @property
    def id(self):
        return self.send()

    @property
    def frozen(self):
        return self._request_id is not None
    
    @property
    def payload(self):
        if self._request_id is not None:
            return self.sent_payload
        # TODO
        return {
            "api_key": api_key,
            "test": {
                "fmf": {
                    "url": git_url,
                    "ref": git_branch,
                    "path": git_path,
                    "name": plan,
                    "plan_filter": planfilter,
                    "test_filter": testfilter,
                }
            },
            "environments": [
                {
                    "arch": architecture,
                    "os": {"compose": compose},
                    "pool": pool,
                    "variables": {
                        "SOURCE_RELEASE": source_release,
                        "TARGET_RELEASE": target_release,
                    },
                    "artifacts": [
                        {
                            "id": artifact_id,
                            "type": artifact_type,
                            "packages": [package],
                        }
                    ],
                    "settings": {
                        "provisioning": {
                            "post_install_script": POST_INSTALL_SCRIPT,
                            "tags": {"BusinessUnit": CLOUD_RESOURCES_TAG},
                        }
                    },
                    "tmt": {
                        "context": {
                            "distro": tmt_distro,
                            "arch": tmt_architecture,
                        }
                    },
                }
            ],
        }

    @property
    def sent_payload(self):
        self.send()
        # TODO

    def iter_results(self):
        self.send()
        # TODO
    
    @property
    def results(self):
        return TFResultsList(self.iter_results())

    def wait(self, timeout=-1):
        self.send()
        # TODO
        return False

    def send(self):
        if self._request_id is not None:
            return self._request_id
        # TODO
        self._request_id = 'UUID'
        return self._request_id

    def __eq__(self, other):
        if self._request_id != other._request_id:
            return False
        for propname in self.PROPERTIES:
            if getattr(self, propname) != getattr(other, propname):
                return False
        return True

class TFRequestsList(list):
    def iter_results(self):
        for request in self:
            for result in request.iter_results():
                yield result

    @property
    def results(self):
        return TFResultsList(self.iter_results())
