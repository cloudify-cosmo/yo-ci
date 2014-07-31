import requests
import json


class TravisCI():
    def __init__(self, config=None):
        self.api_url = config['api_url']
        self.repos_uri = config['repos_uri']
        self.builds_uri = config['builds_uri']
        self.users_uri = config['users_uri']
        self.logs_uri = config['logs_uri']
        self.accounts_uri = config['accounts_uri']
        self.auth_github = config['auth_github']
        self.auth_handshake = config['auth_handshake']
        self.repos_url = self.api_url + self.repos_uri
        self.builds_url = self.api_url + self.builds_uri
        self.users_url = self.api_url + self.users_uri
        self.logs_url = self.api_url + self.logs_uri
        self.accounts_url = self.api_url + self.accounts_uri
        self.github_auth_url = self.api_url + self.auth_github
        self.github_handshake_url = self.api_url + self.auth_handshake

        self.user_agent = 'MyClient/1.0.0'
        self.accept = 'application/vnd.travis-ci.2+json'
        self.token = config['auth_token']

        if self.token:
            r_token = requests.post(
                self.github_auth_url, data={'github_token': self.token})
            if r_token.status_code == requests.codes.NOT_FOUND:
                raise AttributeError("token problem")
            self.auth_token = json.loads(r_token.content)
            r_hs = requests.get(self.github_handshake_url)
            if r_hs.status_code == requests.codes.NOT_FOUND:
                raise AttributeError("token problem2")

        self.headers = {'Accept': self.accept, 'User-Agent': self.user_agent}

    def get_repo(self, id='nir0s/feeder'):
        params = {
            "User-Agent": self.user_agent,
            "Accept": self.accept,
            "Authorization": self.token
        }
        r = requests.get('{0}/{1}'.format(self.repos_url, id), params=params)

        if r.status_code == requests.codes.NOT_FOUND:
            raise AttributeError("Repository with id {} not found!".format(
                str(self._id)))
        for key, value in r.json().items():
            print '{}: {}'.format(key, value)

    def get_users(self):
        # GET /users/ HTTP/1.1
        # User-Agent: MyClient/1.0.0
        # Accept: application/vnd.travis-ci.2+json
        # Authorization: w3NmKXSP1QdzM2PVVFPw
        # Host: api.travis-ci.org
        # {"hello":"world"}

        r = requests.get('{0}'.format(
            self.users_url), params=self.auth_token, headers=self.headers)

        if not r.status_code == 200:
            raise RuntimeError('request failed with error: {}'.format(
                r.status_code))
        if r.status_code == requests.codes.NOT_FOUND:
            raise AttributeError("Repository with id {} not found!".format(
                str(self._id)))

        self.users = r.json()
        return self.users
