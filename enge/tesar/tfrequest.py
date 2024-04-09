import json
import requests

from .common import Freezable, FrozenException, freezable
from .tfresult import TFResult, TFResultsList

class TFEnvironment(Freezable):
    FREEZABLE_PROPERTIES = {
        'parent_request' : None,
        'arch' : None,
        'os_compose' : None,
        'pool' : None,
        'variables' : {},
        'artifacts' : None,
        'settings_provisioning_post_install_script' : None,
        'settings_provisioning_tags' : {},
        'tmt_context' : {},
    }

    def __init__(self, arch, os_compose, pool=None, variables=None, artifacts=None, settings_provisioning_post_install_script=None, settings_provisioning_tags=None, tmt_context=None, parent_request=None):
        super().__init__()
        self.arch = arch
        self.os_compose = os_compose
        self.pool = pool
        self.variables = variables
        self.artifacts = artifacts
        self.settings_provisioning_post_install_script = settings_provisioning_post_install_script
        self.settings_provisioning_tags = settings_provisioning_tags
        self.tmt_context = tmt_context # distro, arch
        self.parent_request = parent_request # needs to be the last to allow creating TFEnvironment instance for already submitted request

    @property
    def frozen(self):
        if self._parent_request is None:
            return False
        return self._parent_request.frozen

class TFRequest(Freezable):
    FREEZABLE_PROPERTIES = {
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
        super().__init__()
        self._request_id = request_id
        self._setup_properties(**kwargs)

    def _setup_properties(self, **kwargs):
        for propname, value in kwargs.items():
            setattr(self, propname, value)

    def copy(self, **kwargs):
        copy_properties = kwargs.copy()
        for propname in self.FREEZABLE_PROPERTIES:
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
        return super().__eq__(other)


class TFRequestsList(list):
    def iter_results(self):
        for request in self:
            for result in request.iter_results():
                yield result

    @property
    def results(self):
        return TFResultsList(self.iter_results())
