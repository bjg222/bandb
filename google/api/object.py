'''
Created on May 2, 2017

@author: wjgallag
'''

class Object(object):
    
    _resource = None
    
    def __init__(self, resource):
        self._resource = resource
        
    def __getattr__(self, name):
        attr = getattr(self._resource, name)
        def wrapper(*args, **kwargs):
#             print(name)
#             print(attr)
#             print(args)
#             print(kwargs)
            return attr(*args, **kwargs)
        return wrapper
