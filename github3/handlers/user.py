#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# author: David Medina

from .base import Handler
import ..models as models
from ..converters import Rawlizer

class User(Handler):
    """ User handler with public access """

    prefix = 'users'

    def __repr__(self):
        return '<User handler> %s>' % getattr(self, 'username', 'without user')

    def set_username(self, user):
        """
        Set username to query public handler

        :param `user`: User model or username string
        """

        parse_user = str(getattr(user, 'login', user))
        self.username = parse_user
        self.prefix = '/'.join((self.prefix, parse_user))

    def get(self):
        """ Return user """

        return self._get_resource('', model=models.User)

    def get_followers(self):
        """ Return user's followers """

        return self._get_resources('followers', model=models.User)

    def get_following(self):
        """ Return users that follow """

        return self._get_resources('following', model=models.User)

    def get_repos(self):
        """ Return user's public repositories """

        return self._get_resources('repos', model=models.Repo)

    def get_watched(self):
        """ Return repositories that user whatch """

        return self._get_resources('watched', model=models.Repo)

    def get_orgs(self):
        """ Return user's public organizations """

        return self._get_resources('orgs', model=models.Org)

    def get_gists(self):
        """ Return user's gists """

        return self._get_resources('gists', model=models.Gist)

class AuthUser(User):
    """ User handler with public and private access """

    prefix = 'user'

    def __repr__(self):
        return '<AuthUser handler> %s>' % self._gh.session.auth[0]

    def get(self):
        return self._get_resource('', model=models.AuthUser)

    def get_emails(self):
        """ Return list of emails """

        # Ignore converter, it must be Rawlizer
        emails = self._get_resource('emails', converter=Rawlizer())
        return emails

    def create_emails(self, *args):
        """
        Add emails

        :param args: Collection of emails
            create_emails(*('test1@example.com', 'test2@example.cm'))
        """
        parsed_emails = map(str, args)
        all_mails = self._post_resource(
            'emails', data=parsed_emails, converter=Rawlizer())
        return all_mails

    def delete_emails(self, *args):
        """
        Delete emails

        :param args: Collection of emails
            create_emails(*('test1@example.com', 'test2@example.cm'))
        """
        parsed_emails = map(str, args)
        return self._delete('emails', data=parsed_emails)

    def is_following(self, user):
        """
        Return true if you are following the user

        :param `user`: User model or username string
        """

        parse_user = str(getattr(user, 'login', user))
        return self._bool('following/%s' % parse_user)

    def follow(self, user):
        """
        Follow user

        :param `user`: User model or username string
        """

        parse_user = str(getattr(user, 'login', user))
        return self._put('following/%s' % parse_user)

    def unfollow(self, user):
        """
        Unfollow user

        :param `user`: User model or username string
        """

        parse_user = str(getattr(user, 'login', user))
        return self._delete('following/%s' % parse_user)

    def get_keys(self):
        """ Get public keys """

        return self._get_resources('keys', model=models.Key)

    def get_key(self, key_id):
        """ Get public key by id """

        return self._get_resource('keys/%s' % key_id, model=models.Key)

    def create_key(self, **kwargs):
        """
        Create public key

        :param title
        :param key: Key string
        """

        #TODO: render key.pub file
        key = {
            'title': kwargs.get('title',''),
            'key': kwargs.get('key','')
        }
        return self._post_resource('keys', data=key, model=models.Key)

    def delete_key(self, key_id):
        """ Delete public key """

        return self._delete('keys/%s' % key_id)

    def get_repos(self, filter='all'):
        """
        Return user's public repositories

        param: filter: 'all', 'public', 'private' or 'member'
        """

        return self._get_resources('repos', model=models.Repo,
                                   type=str(filter))

    def is_watching_repo(self, owner, repo):
        """
        Return true if you are watching the user repository

        :param owner: username
        :param repo: repository name
            is_watching_repo('copitux', 'python-github3')
        """

        owner = getattr(owner, 'login', owner)
        repo = getattr(repo, 'name', repo)
        return self._bool('watched/%s/%s' % (owner, repo))

    def watch_repo(self, owner, repo):
        """
        Watch the repository

        :param owner: username
        :param repo: repository name
        """

        return self._put('watched/%s/%s' % (owner, repo))

    def unwatch_repo(self, owner, repo):
        """
        Unwatch the repository

        :param owner: username
        :param repo: repository name
        """

        return self._delete('watched/%s/%s' % (owner, repo))
