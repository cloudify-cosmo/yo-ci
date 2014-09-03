import requests
import json
from utils import import_config

USER_AGENT = 'MyClient/1.0.0'
ACCEPT = 'application/vnd.travis-ci.2+json'
LOG_ACCEPT = 'text/plain'
HEADERS = {'Accept': ACCEPT, 'User-Agent': USER_AGENT}
LOG_HEADERS = {
    'Accept': LOG_ACCEPT,
    'User-Agent': USER_AGENT
}

DEFAULT_CONFIG_PATH = '/home/nir0s/repos/yo-ci/yoci/config.yml'

C = import_config(DEFAULT_CONFIG_PATH)
C = C['Travis']
GITHUB_AUTH_URL = C['api_url'] + C['auth_github']
GITHUB_HANDSHAKE_URL = C['api_url'] + C['auth_handshake']
TOKEN = C['auth_token']


def get_token(lgr, auth_url, hs_url, token):
    lgr.debug('requesting for auth token from: {} with token: {}'.format(
        auth_url, TOKEN))
    r_token = requests.post(auth_url, data={'github_token': TOKEN})
    if r_token.status_code == requests.codes.NOT_FOUND:
        raise AttributeError("token problem")
    lgr.debug('token is: {}'.format(r_token.json()['access_token']))
    return json.loads(r_token.content)
    r_hs = requests.get(hs_url)
    if r_hs.status_code == requests.codes.NOT_FOUND:
        raise AttributeError("token problem2")


class Users:
    def __init__(self, lgr, c=None, auth_token=None, id=None):
        # if config is given, use it, if not, use default
        c = c if c else C
        # if authentication token is given, use it, if not request for one
        auth_token = auth_token if auth_token else \
            get_token(lgr, GITHUB_AUTH_URL, GITHUB_HANDSHAKE_URL, TOKEN)
        # define request url
        url = c['api_url'] + c['users_uri']
        # test for missing properties
        if not id:
            raise RuntimeError('user must be specified')

        # request data
        lgr.debug('Travis: requesting for users from: {}'.format(url))
        r = requests.get(url, params=auth_token, headers=HEADERS)
        if not r.status_code == 200:
            raise RuntimeError('request failed with error: {}'.format(
                r.status_code))

        # set properties
        # lgr.debug(r.json(), sort_keys=True, indent=4, separators=(',', ': '))
        p = r.json()['user']
        self.name = p['name']
        self.locale = p['locale']
        self.created_at = p['created_at']
        self.synced_at = p['synced_at']
        self.id = p['id']
        self.correct_scopes = p['correct_scopes']
        self.gravatar_id = p['gravatar_id']
        self.is_syncing = p['is_syncing']
        self.login = p['login']
        self.email = p['email']


class Repo:
    def __init__(self, lgr, c=None, auth_token=None, id=None):
        # if config is given, use it, if not, use default
        c = c if c else C
        # if authentication token is given, use it, if not request for one
        auth_token = auth_token if auth_token else \
            get_token(lgr, GITHUB_AUTH_URL, GITHUB_HANDSHAKE_URL, TOKEN)
        # define request url
        url = c['api_url'] + c['repos_uri'] + id
        # test for missing properties
        if not id:
            raise RuntimeError('repo must be specified')

        # request data
        lgr.debug('Travis: requesting for repo from: {}'.format(url))
        r = requests.get(url, params=auth_token, headers=HEADERS)
        if r.status_code == requests.codes.NOT_FOUND:
            raise AttributeError("repo {0} not found!".format(id))
        if not r.status_code == 200:
            raise RuntimeError('request failed with error: {}'.format(
                r.status_code))

        # set properties
        p = r.json()['repo']
        self.id = p['id']
        self.slug = p['slug']
        self.description = p['description']
        self.last_build_id = p['last_build_id']
        self.last_build_number = p['last_build_number']
        self.last_build_state = p['last_build_state']
        self.last_build_duration = p['last_build_duration']
        self.last_build_started_at = p['last_build_started_at']
        self.last_build_finished_at = p['last_build_finished_at']
        self.github_language = p['github_language']

        lgr.debug('last build is: {}'.format(self.last_build_id))
        self.last_build = Build(lgr, c, auth_token, self.last_build_id)


class Builds:
    def __init__(self, lgr, c=None, auth_token=None, repo=None):
        # if config is given, use it, if not, use default
        self.c = c if c else C
        # if authentication token is given, use it, if not request for one
        self.auth_token = auth_token if auth_token else \
            get_token(lgr, GITHUB_AUTH_URL, GITHUB_HANDSHAKE_URL, TOKEN)
        # define request url
        url = \
            self.c['api_url'] + self.c['repos_uri'] + repo + '/' + \
            self.c['builds_uri'][0:-1]
        # test for missing properties
        if not repo:
            raise RuntimeError('repo must be specified')

        self.lgr = lgr

        # request data
        lgr.debug('Travis: requesting for build from: {}'.format(url))
        r = requests.get(url, params=auth_token, headers=HEADERS)
        if r.status_code == requests.codes.NOT_FOUND:
            raise AttributeError("builds for repo {0} not found!".format(repo))
        if not r.status_code == 200:
            raise RuntimeError('request failed with error: {}'.format(
                r.status_code))

        # set properties
        # lgr.debug(json.dumps(
        #     r.json(), sort_keys=True, indent=4, separators=(',', ': ')))
        p = r.json()
        self.commits = p['commits']
        self.builds = p['builds']

    def get_job_status(self, sha_id):
        commit_id = self._get_commit_id(sha_id)
        if commit_id is None:
            raise RuntimeError('Could not find commit matching to sha {0}'
                               .format(sha_id))

        jobs_ids = self._get_job_ids(commit_id)
        if jobs_ids is None:
            raise RuntimeError('Could not retrieve job ids for sha {0}.'
                               ' This should not happen'.format(sha_id))

        jobs_state = dict()
        for job_id in jobs_ids:
            job = Job(self.lgr, self.c, self.auth_token, job_id)
            jobs_state.update({job_id: job.state})

        return jobs_state

    def _get_commit_id(self, sha_id):
        for commit in self.commits:
            if commit['sha'] == sha_id:
                return commit['id']

    def _get_job_ids(self, commit_id):
        for build in self.builds:
            if build['commit_id'] == commit_id:
                return build['job_ids']


class Build:
    def __init__(self, lgr, c=None, auth_token=None, id=None):
        # if config is given, use it, if not, use default
        c = c if c else C
        # if authentication token is given, use it, if not request for one
        auth_token = auth_token if auth_token else \
            get_token(lgr, GITHUB_AUTH_URL, GITHUB_HANDSHAKE_URL, TOKEN)
        # define request url
        url = c['api_url'] + c['builds_uri'] + str(id)
        # test for missing properties
        if not id:
            raise RuntimeError('build id must be specified')

        # request data
        lgr.debug('Travis: requesting for build from: {}'.format(url))
        r = requests.get(url, params=auth_token, headers=HEADERS)
        if r.status_code == requests.codes.NOT_FOUND:
            raise AttributeError("build {0} not found!".format(id))
        if not r.status_code == 200:
            raise RuntimeError('request failed with error: {}'.format(
                r.status_code))

        # set properties
        # lgr.debug(json.dumps(
        #     r.json(), sort_keys=True, indent=4, separators=(',', ': ')))
        p = r.json()
        self.commit = p['commit']
        self.build = p['build']
        self.annotations = p['annotations']
        self.jobs = []
        job_ids = [job['id'] for job in p['jobs']]
        lgr.debug('list of jobs for build {} is: {}'.format(id, job_ids))
        for job in p['jobs']:
            self.jobs.append(Job(lgr, c, auth_token, job['id']))


class Job:
    def __init__(self, lgr, c=None, auth_token=None, id=None):
        # if config is given, use it, if not, use default
        c = c if c else C
        # if authentication token is given, use it, if not request for one
        auth_token = auth_token if auth_token else \
            get_token(lgr, GITHUB_AUTH_URL, GITHUB_HANDSHAKE_URL, TOKEN)
        # define request url
        url = c['api_url'] + c['jobs_uri'] + str(id)
        # test for missing properties
        if not id:
            raise RuntimeError('build id must be specified')

        # request data
        lgr.debug('Travis: requesting for job from: {}'.format(url))
        r = requests.get(url, params=auth_token, headers=HEADERS)
        if r.status_code == requests.codes.NOT_FOUND:
            raise AttributeError("job {0} not found!".format(id))
        if not r.status_code == 200:
            raise RuntimeError('request failed with error: {}'.format(
                r.status_code))

        # set properties
        p = r.json()['job']

        self.allow_failure = p['allow_failure']
        self.annotation_ids = p['annotation_ids']
        self.build_id = p['build_id']
        self.commit_id = p['commit_id']
        self.config = p['config']
        self.finished_at = p['finished_at']
        self.id = p['id']
        self.log_id = p['log_id']
        self.number = p['number']
        self.queue = p['queue']
        self.repository_id = p['repository_id']
        self.repository_slug = p['repository_slug']
        self.started_at = p['started_at']
        self.state = p['state']
        self.tags = p['tags']
        self.log = Log(lgr, c, auth_token, self.log_id).log_data


class Log:
    def __init__(self, lgr, c=None, auth_token=None, id=None):
        # if config is given, use it, if not, use default
        c = c if c else C
        # if authentication token is given, use it, if not request for one
        auth_token = auth_token if auth_token else \
            get_token(lgr, GITHUB_AUTH_URL, GITHUB_HANDSHAKE_URL, TOKEN)
        # define request url
        url = c['api_url'] + c['logs_uri'] + str(id)
        # test for missing properties
        if not id:
            raise RuntimeError('log id must be specified')

        # request data
        lgr.debug('Travis: requesting for log from: {}'.format(url))
        r = requests.get(url, params=auth_token, headers=LOG_HEADERS)
        if r.status_code == requests.codes.NOT_FOUND:
            raise AttributeError("log {0} not found!".format(id))
        if not r.status_code == 200:
            raise RuntimeError('request failed with error: {}'.format(
                r.status_code))

        # set properties
        self.log_data = r.content
