# -*- coding: utf-8 -*-

__all__ = [
    'TimeoutError',
    'PolicyError',
    'InvalidProtocolError',
    'BypassProtocolError'
]

class TimeoutError(BaseException):pass

class PolicyError(Exception): pass

class InvalidProtocolError(PolicyError): pass

class BypassProtocolError(PolicyError): pass

