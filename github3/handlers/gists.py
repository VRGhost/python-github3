#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from .base import Handler, MimeTypeMixin
from .. import models


class Gist(Handler, MimeTypeMixin):
    """ Gist handler with public access """

    prefix = 'gists'

    def __repr__(self):
        return '<Gist handler>'

    def all_gists(self, limit=None):
        """ Return all public gists

        NOTE: It returns all gists in github environment. Maybe you
        want to use `limit` parameter
        """

        return self._get_resources('', model=models.Gist, limit=limit)

    def get(self, gist_id):
        """ Return gist

        param `gist_id`: Gist id
        """

        return self._get_resource(gist_id, model=models.Gist)

    def get_comments(self, gist_id, limit=None):
        """ Return gist's comments

        param `gist_id`: Gist id
        param `limit`: Number of comments
        """

        return self._get_resources('%s/comments' % gist_id,
            model=models.GistComment, limit=limit,
            headers=self.mime_header())

    def get_comment(self, comment_id):
        """ Return gist's comment

        param `comment_id`: Comment id
        """

        return self._get_resource('comments/%s' % comment_id,
            model=models.GistComment, headers=self.mime_header())


class AuthGist(Gist):

    def all_gists(self, limit=None):
        """ Return all public gists

        NOTE: It returns all gists in github environment. Maybe you
        want to use `limit` parameter
        """

        return self._get_resources('public', model=models.Gist, limit=limit)

    def my_gists(self, limit=None):
        """ Return authenticated user's gists

        param `limit`: Number of gists
        """

        return self._get_resources('', model=models.Gist, limit=limit)

    def my_starred_gists(self, limit=None):
        """ Return authenticated user's starred gists

        param `limit`: Number of gists
        """

        return self._get_resources('starred', model=models.Gist, limit=limit)

    def create_gist(self, is_public, files, desc=None):
        """ Create and return a gist """

        data = {
            'public': bool(is_public),
            'files': files,  # TODO: Issue #1
            'desc': desc or '',
        }
        return self._post_resource('', data=data, model=models.Gist)

    def star_gist(self, gist_id):
        """ Star a gist

        param `gist_id`: Gist id to star
        """

        return self._put('%s/star' % gist_id)

    def unstar_gist(self, gist_id):
        """ Unstar a gist

        param `gist_id`: Gist id to unstar
        """

        return self._delete('%s/star' % gist_id)

    def is_starred(self, gist_id):
        """ True if gist is starred

        param `gist_id`: Gist id
        """

        return self._bool('%s/star' % gist_id)

    def fork_gist(self, gist_id):
        """ Return forked gist from id

        param `gist_id`: Gist id to be forked...
        """

        return self._post_resource('%s/fork' % gist_id, data=None,
                                   model=models.Gist)

    def delete_gist(self, gist_id):
        """ Delete the gist

        param `gist_id`: Gist id
        """

        return self._delete(str(gist_id))

    def create_comment(self, gist_id, comment):
        """ Create comment into gist """

        data = {'body': comment}
        return self._post_resource('%s/comments' % gist_id, data=data,
                            model=models.GistComment)

    def delete_comment(self, comment_id):
        """ Delete comment

        param `comment_id`: Comment id
        """

        return self._delete('comments/%s' % comment_id)
