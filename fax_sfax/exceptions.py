# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from json import dumps


class DataException(Exception):
    error = None
    description = None
    status = 500
    headers = {}

    def __init__(self):
        super(DataException, self).__init__(self.error)

    def to_dict(self):
        return {
            'error': self.error,
            'error_description': self.description,
        }

    def __str__(self, ):
        return dumps(self.to_dict())


class AuthenticationException(Exception):
    error = None
    description = None
    status = 400
    headers = {}

    def __init__(self):
        super(AuthenticationException, self).__init__(self.error)

    def to_dict(self):
        return {
            'error': self.error,
            'error_description': self.description,
        }


class InvalidTokenException(AuthenticationException):
    status = 403
    error = 'invalid_token'
    description = 'Invalid token provided in request'


class MultipleTransmissionException(DataException):
    error = 'multiple_transmission'
    description = 'Multiple transmissions found matching provided FaxID'


class NoTransmissionException(DataException):
    status = 404
    error = 'no_transmission'
    description = 'No transmission found matching provided FaxID'


class NoOperationException(DataException):
    error = 'noop_error'
    description = 'Server error, no operation was triggered'
