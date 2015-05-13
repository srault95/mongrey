# -*- coding: utf-8 -*-

__all__ = [
    'TimeoutError',
    'PolicyError',
    'InvalidProtocolError',
    'BypassProtocolError',
    'ConfigurationError'
]


class TimeoutError(BaseException): pass


class ConfigurationError(Exception): pass


class PolicyError(Exception): pass


class InvalidProtocolError(PolicyError): pass


class BypassProtocolError(PolicyError): pass

class ValidationError(AssertionError):

    def __init__(self, message="", **kwargs):
        self.field_name = kwargs.get('field_name', None)
        self.message = message
        
    def __str__(self):
        return unicode(self.message)

    def __unicode__(self):
        return self.message

