import requests
import json
from yoci.utils import import_config

USER_AGENT = 'MyClient/1.0.0'
ACCEPT = 'application/vnd.travis-ci.2+json'
LOG_ACCEPT = 'text/plain'
HEADERS = {'Accept': ACCEPT, 'User-Agent': USER_AGENT}
LOG_HEADERS = {
    'Accept': LOG_ACCEPT,
    'User-Agent': USER_AGENT
}

DEFAULT_CONFIG_PATH = '../config.yml'

C = import_config(None)['Travis']


def get_token(lgr, auth_url, hs_url, token):
    lgr.debug('requesting for auth token from: {} with token: {}'.format(
        auth_url, token))
    r_token = requests.post(auth_url, data={'github_token': token})
    if r_token.status_code == requests.codes.NOT_FOUND:
        raise AttributeError("token problem")
    lgr.debug('token is: {}'.format(r_token.json()['access_token']))
    return json.loads(r_token.content)
    r_hs = requests.get(hs_url)
    if r_hs.status_code == requests.codes.NOT_FOUND:
        raise AttributeError("token problem2")


def default_props(func):
    def inner(*args, **kwargs):
        c = kwargs.get('c', None)
        # if config is given, use it, if not, use default
        c = c if c else C
        kwargs.update({'c': c})
        auth_token = kwargs.get('auth_token', None)
        # if authentication token is given, use it, if not request for one
        if not auth_token:
            github_auth_url = c['api_url'] + c['auth_github']
            github_handshake_url = c['api_url'] + c['auth_handshake']
            auth_token = c['auth_token']
            lgr = args[1]
            auth_token = get_token(lgr, github_auth_url, github_handshake_url,
                                   c['auth_token'])
        kwargs.update({'auth_token': auth_token})
        return func(*args, **kwargs)
    return inner


def get(url, auth_token, lgr, *args):
    # request data
    lgr.debug('GET >> {0}'.format(url))
    res = requests.get(url, params=auth_token, headers=HEADERS)
    if res.status_code == requests.codes.NOT_FOUND:
        raise AttributeError('Request url {0} returned 404 Not Found'
                             .format(url))
    if not res.status_code == 200:
        raise RuntimeError('Request url {0} failed with error: {1}:{2}'.format(
            res.status_code, res.reason, url))

    return res


class Users:
    @default_props
    def __init__(self, lgr, c=None, auth_token=None, id=None):
        self.c = c
        self.auth_token = auth_token
        self.id = id
        self.lgr = lgr

    def show_user(self, id):
        if not id:
            id = self.id
            if not self.id:
                raise RuntimeError('User ID must be specified')
        url = self.c['api_url'] + self.c['users_uri'] + str(id)
        response = get(url, self.auth_token, self.lgr)

        return response['user']


class Repositories:
    @default_props
    def __init__(self, lgr, c=None, auth_token=None, repo_id=None):
        self.c = c
        self.auth_token = auth_token
        self.repo_id = repo_id
        self.lgr = lgr

    def show_repo(self, repo_id):
        if not repo_id:
            repo_id = self.repo_id
            if not self.repo_id:
                raise RuntimeError('repo must be specified')
        url = self.c['api_url'] + self.c['repos_uri'] + str(repo_id)
        response = get(url, self.auth_token, self.lgr)

        return response.json()['repo']

    def list_repos_with_recent_activity(self):
        url = self.c['api_url'] + self.c['repos_uri']
        response = get(url, self.auth_token, self.lgr)

        return response.content


class Builds:
    @default_props
    def __init__(self, lgr, c=None, auth_token=None, repo=None):
        self.c = c
        self.auth_token = auth_token
        self.repo = repo
        self.lgr = lgr

    def list_builds(self, repo=None):
        if not repo:
            repo = self.repo
            if not self.repo:
                raise RuntimeError('Repository must be specified')
        # define request url
        url = \
            self.c['api_url'] + self.c['repos_uri'] + repo + '/' + \
            self.c['builds_uri'][0:-1]
        response = get(url, self.auth_token, self.lgr)

        return response.json()['builds'], response.json()['commits']

    def show_build(self, id=None):
        if not id:
            raise RuntimeError('Build id must be specified')
        url = self.c['api_url'] + self.c['builds_uri'] + str(id)
        self.lgr.debug('Travis: requesting for build from: {}'.format(url))
        response = get(url, self.auth_token, self.lgr)

        return response.json()['build']


class Job:
    @default_props
    def __init__(self, lgr, c=None, auth_token=None, job_id=None):
        self.c = c
        self.auth_token = auth_token
        self.job_id = job_id
        self.lgr = lgr

    def show_job(self, job_id=None):
        if not job_id:
            job_id = self.job_id
            if not self.job_id:
                raise RuntimeError('Job ID must be specified')
        url = self.c['api_url'] + self.c['jobs_uri'] + str(job_id)
        response = get(url, self.auth_token, self.lgr)

        return response.json()['job']


class Log:
    @default_props
    def __init__(self, lgr, c=None, auth_token=None, log_id=None):
        self.c = c
        self.auth_token = auth_token
        self.lgr = lgr
        self.log_id = log_id

    def show_log(self, log_id):
        if not log_id:
            log_id = self.log_id
            if not self.log_id:
                raise RuntimeError('log ID must be specified')
        url = self.c['api_url'] + self.c['logs_uri'] + str(log_id)
        response = get(url, self.auth_token, self.lgr)

        return response.content
