'''
Created on May 2, 2017

@author: wjgallag
'''

from googleapiclient import discovery


class Client(object):
    
    _api = None
    
    _creds = None
    _auth = None
    
    _serv = None
    
    def __init__(self, creds, api = None):
        self._creds = creds
        self._api = api
    
    def login(self):
        if (not self._creds.is_authorized()):
            self._creds.authorize()
        self._auth = self._creds.get_authorization()
        return self
    
    def build(self, name=None, version=None):
        if (self._api is not None):
            name = self._api.get_name()
            version = self._api.get_version()
        self._serv = discovery.build(name, version, http=self._auth)
        if (self._api is not None):
            self._api = self._api(self._serv)
        return self
    
    def __getattr__(self, name):
        attr = getattr(self._api if self._api is not None else self._serv, name)
        def wrapper(*args, **kwargs):
#             print(name)
#             print(attr)
#             print(args)
#             print(kwargs)
            return attr(*args, **kwargs)
        return wrapper
    