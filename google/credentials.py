'''
Created on May 2, 2017

@author: wjgallag
'''

import abc

from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

#TODO: Credential storage

class CredentialHolder(abc.ABC):

    _credentials = None
    _authorization = None

    def __init__(self):
        self._make_credentials()

    @abc.abstractmethod
    def _make_credentials(self):
        pass

    def authorize(self):
        if (not self.is_authorized()):
            self._authorization = self._credentials.authorize(Http())

    def get_credentials(self):
        return self._credentials

    def is_authorized(self):
        #TODO: actually check that this is the right way do this or what the best way to figure it out is
        return self._authorization is not None

    def get_authorization(self):
        return self._authorization


class ServiceAccount(CredentialHolder):

    _keyfile = None
    _scope = None

    def __init__(self, keyfile, scope):
        self._keyfile = keyfile
        self._scope = scope
        CredentialHolder.__init__(self)

    def _make_credentials(self):
        self._credentials = ServiceAccountCredentials.from_json_keyfile_dict(self._keyfile, self._scope)
