#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from ..core import Paginate
from ..converters import Modelizer


class MimeTypeMixin(object):

    VERSION = 'beta'

    def __init__(self):
        self.mimetypes = set()

    def _parse_mime_type(self, type):
        return 'application/vnd.github.%s.%s+json' % (
            self.VERSION, type)

    def add_raw(self):
        self.mimetypes.add(self._parse_mime_type('raw'))
        return self

    def add_text(self):
        self.mimetypes.add(self._parse_mime_type('text'))
        return self

    def add_html(self):
        self.mimetypes.add(self._parse_mime_type('html'))
        return self

    def add_full(self):
        self.mimetypes.add(self._parse_mime_type('full'))
        return self

    def mime_header(self):
        if self.mimetypes:
            return {'Accept': ', '.join(self.mimetypes)}
        return None


class Handler(object):
    """ Handler base. Requests to API and modelize responses """

    def __init__(self, gh):
        self._gh = gh
        super(Handler, self).__init__()

    def _inject_handler(self, handler, prefix=''):
        import inspect
        for method, callback in inspect.getmembers(handler):
            if method.startswith(prefix) and inspect.ismethod(callback):
                setattr(self, method, callback)

    def _prefix_resource(self, resource):
        prefix = getattr(self, 'prefix', '')
        return '/'.join((prefix, str(resource))).strip('/')

    def _get_converter(self, kwargs={}):
        converter = kwargs.pop(
            'converter',  # 1. in kwargs
            getattr(self, 'converter',  # 2. in handler
            Modelizer))  # 3. Default

        return converter()

    def _put(self, resource, **kwargs):
        """ Put proxy request"""

        return self._bool(resource, method='put', **kwargs)

    def _delete(self, resource, **kwargs):
        """ Delete proxy request"""

        return self._bool(resource, method='delete', **kwargs)

    def _bool(self, resource, **kwargs):
        """ Handler request to boolean response """

        from ..exceptions import NotFound
        resource = self._prefix_resource(resource)
        try:
            callback = getattr(self._gh, kwargs.get('method', ''),
                               self._gh.head)
            response = callback(resource, **kwargs)
        except NotFound:
            return False
        assert response.status_code == 204
        return True

    def _get_resources(self, resource, model=None, limit=None, **kwargs):
        """ Hander request to multiple resources """

        if limit:
            limit = abs(limit)
        resource = self._prefix_resource(resource)
        converter = self._get_converter(kwargs)
        counter = 1
        for page in Paginate(resource, self._gh.get, **kwargs):
            for raw_resource in page:
                counter += 1
                converter.inject(model)
                yield converter.loads(raw_resource)
                if limit and counter > limit:
                    break
            else:
                continue
            break

    def _get_resource(self, resource, model=None, **kwargs):
        """ Handler request to single resource """

        resource = self._prefix_resource(resource)
        converter = self._get_converter(kwargs)
        raw_resource = self._gh.get(resource, **kwargs)
        converter.inject(model)
        return converter.loads(raw_resource)

    def _post_resource(self, resource, data, model=None, **kwargs):
        """ Handler request to create a resource """

        resource = self._prefix_resource(resource)
        raw_resource = self._gh.post(resource, data=data)
        converter = self._get_converter(kwargs)
        converter.inject(model)
        return converter.loads(raw_resource)
