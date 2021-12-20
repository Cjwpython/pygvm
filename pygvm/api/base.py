# coding: utf-8

import weakref


class BaseAPI(object):
    """base api client"""

    def __init__(self, apiset):
        self._apiset = weakref.ref(apiset)
        self.init()

    def init(self):
        pass

    def prepare(self):
        """invoke after login by apiset"""
        pass

    @property
    def api(self):
        """actually apiset"""
        return self._apiset()

    @property
    def client(self):
        """http client"""
        return self.api.client

    @property
    def token(self):
        return self.api.client.token

    @property
    def session(self):
        return self.api.client.session

    @property
    def base_url(self):
        return self.api.base_url

    def list_recovery(self, data):
        """列表恢复"""
        if data is None:
            return []
        if type(data) == list:
            return data
        return [data]


class APISet(object):
    def __init__(self):
        self._apis = {}
        self.token = None
        self.base_url = None
        self._client = None

    def register(self, name):
        def cls_wrapper(cls):
            if name in self._apis:
                raise KeyError('class {} need an unique name: {}'.format(cls, name))
            # import ipdb; ipdb.set_trace()
            inst = cls(self)
            self._apis[name] = inst
        return cls_wrapper

    def set_client(self, client):
        self._client = weakref.ref(client)

    @property
    def client(self):
        return self._client()

    def set_base_url(self, base_url):
        self.base_url = base_url

    def prepare(self):
        """invoke after login"""
        for inst in self._apis.values():
            inst.prepare()

    def __getattr__(self, name):
        if name in self._apis:
            return self._apis[name]
        return getattr(super(APISet, self), name)


APISET = APISet()
