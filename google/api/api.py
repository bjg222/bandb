'''
Created on May 2, 2017

@author: wjgallag
'''

from google.api.object import Object

class Api(Object):
    
    @classmethod
    def get_name(cls):
        return cls._name
    
    @classmethod
    def get_version(cls):
        return cls._version