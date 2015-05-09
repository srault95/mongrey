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

