#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json

from . import exceptions

class GithubError(object):
    """ Handler for API errors """

    def __init__(self, response):
        self._parser = json
        self.status_code = response.status_code
        try:
            self.debug = self._parser.loads(response.content)
        except (ValueError, TypeError):
            self.debug = {'message': response.content}

    def error_400(self):
        return exceptions.BadRequest("400 - %s" % self.debug.get('message'))

    def error_401(self):
        return exceptions.Unauthorized("401 - %s" % self.debug.get('message'))

    def error_404(self):
        return exceptions.NotFound("404 - %s" % self.debug.get('message'))

    def error_422(self):
        errors = self.debug.get('errors')
        if errors:
            errors = ['{resource}: {code} => {field}'.format(**error)
                      for error in errors]
        return exceptions.UnprocessableEntity(
            '422 - %s %s' % (self.debug.get('message'), errors))

    def process(self):
        raise_error = getattr(self, 'error_%s' % self.status_code, False)
        if raise_error:
            raise raise_error()
